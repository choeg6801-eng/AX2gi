import os
import requests
import streamlit as st
from dotenv import load_dotenv

# 1. 환경 변수 로드
load_dotenv() 
WEATHER_API_KEY = os.getenv("openweather_API_key")
EXCHANGE_API_KEY = os.getenv("exchange_API_key")

# 2. 페이지 설정
st.set_page_config(page_title="글로벌 비즈니스 & 여행 대시보드", page_icon="🌍", layout="wide")

# 3. 커스텀 CSS (목록바 글자 크기를 더 크게 키우고 박스 높이 조정)
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #F4F9F4;
}
/* 세계지도 배경에 연두색 필터 및 투명도 적용 */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; 
    left: 0; 
    width: 100%; 
    height: 100%;
    background-image: url("https://upload.wikimedia.org/wikipedia/commons/8/80/World_map_-_low_resolution.svg");
    background-size: cover;
    background-position: center;
    opacity: 0.25;
    filter: invert(75%) sepia(40%) saturate(600%) hue-rotate(50deg);
    z-index: 0;
    pointer-events: none;
}
[data-testid="stHeader"] {
    background-color: rgba(0,0,0,0);
}

/* 💡 목록바(셀렉트박스) 내부 글자 크기를 훨씬 크게 키움 (1.5rem) */
div[data-baseweb="select"] > div {
    border-color: #FF7F50 !important; /* 자몽색 (Coral) */
    border-width: 2px !important;
    border-radius: 12px !important;
    min-height: 65px !important; /* 박스 높이도 글자에 맞춰 키움 */
}
div[data-baseweb="select"] span {
    font-size: 1.5rem !important; /* 글자 크기 대폭 확대 */
    font-weight: 700 !important;
}

.info-card {
    background-color: rgba(248, 249, 250, 0.95);
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 20px;
    height: 100%;
    position: relative;
    z-index: 1;
}
.metric-container {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    margin-top: 10px;
}
.metric-box {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 15px;
    margin: 5px;
    flex: 1;
    min-width: 100px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.metric-value {
    font-size: 1.2rem;
    font-weight: bold;
    color: #333333;
}
.metric-label {
    font-size: 0.9rem;
    color: #666666;
    margin-top: 5px;
}
.analysis-container {
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin-top: 15px;
    position: relative;
    z-index: 1;
}
.analysis-box {
    background-color: rgba(255, 255, 255, 0.95);
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    border-left: 6px solid #4A90E2;
}
.analysis-title {
    font-size: 1.1rem;
    font-weight: bold;
    color: #2C3E50;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.analysis-content {
    font-size: 0.95rem;
    color: #4A5568;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

# 4. 지원 국가 데이터
LOCATION_DATA = {
    "미국 (뉴욕)": {
        "city": "New York", "currency": "USD", "symbol": "$", 
        "base_rate": 1350, "price_level": "약 140% (주거 및 외식비가 매우 높음)", 
        "trade_tip": "주요 수출품: 자동차, 기계류. 통상 압박(IRA 등) 모니터링 필수. 비즈니스 미팅 시 결론부터 말하는 직설적인 화법을 선호합니다.",
        "packing_tip": "전자기기 멀티탭(110V 전용), 편안한 운동화(도보 이동 많음), 일교차 대비 겉옷",
        "must_visit": "센트럴 파크, 타임스퀘어, 브로드웨이 뮤지컬 관람, 메트로폴리탄 미술관"
    },
    "독일 (베를린)": {
        "city": "Berlin", "currency": "EUR", "symbol": "€", 
        "base_rate": 1450, "price_level": "약 110% (마트 장바구니 물가는 저렴하나, 서비스 요금이 높음)", 
        "trade_tip": "주요 수출품: 배터리, 화학제품. CE 인증 등 환경/안전 규제가 매우 엄격합니다. 구두 약속보다 계약서와 문서 증빙을 극도로 중시합니다.",
        "packing_tip": "EU 규격 멀티어댑터, 방수 바람막이(변덕스러운 날씨), 동전 지갑(현금 사용처 간혹 있음)",
        "must_visit": "브란덴부르크 문, 베를린 장벽(이스트 사이드 갤러리), 박물관 섬"
    },
    "일본 (도쿄)": {
        "city": "Tokyo", "currency": "JPY", "symbol": "¥", 
        "base_rate": 900, "price_level": "약 90% (최근 엔저 현상으로 체감 물가가 한국보다 낮음)", 
        "trade_tip": "주요 수출품: 철강, 전자부품. 품질 기준이 까다로우며 신뢰 구축에 오랜 시간이 걸립니다. 대면 미팅과 비즈니스 예절(명함 교환 등)이 매우 중요합니다.",
        "packing_tip": "동전 지갑(동전 사용 빈도가 높음), 돼지코(110V), 편한 슬리퍼(숙소용)",
        "must_visit": "시부야 스크램블, 센소지, 도쿄타워, 신주쿠교엔"
    },
    "영국 (런던)": {
        "city": "London", "currency": "GBP", "symbol": "£", 
        "base_rate": 1700, "price_level": "약 145% (교통비와 런던 내 주거비가 세계 최고 수준)", 
        "trade_tip": "주요 수출품: 승용차, 바이오. 브렉시트(Brexit) 이후 독자적인 영국 인증(UKCA)을 도입했습니다. 간접적이고 우회적인 화법에 주의해야 합니다.",
        "packing_tip": "BF타입 어댑터, 튼튼한 3단 우산(소나기 잦음), 교통카드(컨택리스 카드)",
        "must_visit": "대영박물관, 런던 아이, 타워 브리지, 대회의실 및 빅벤"
    },
    "호주 (시드니)": {
        "city": "Sydney", "currency": "AUD", "symbol": "$", 
        "base_rate": 880, "price_level": "약 130% (외식비, 인건비가 높아 전반적인 서비스 물가 높음)", 
        "trade_tip": "주요 수출품: 석유제품, 자동차. 자원 강국이므로 원자재 수입 비중이 높습니다. 검역(목재, 식품 등)이 세계 최고 수준으로 까다로우니 주의하세요.",
        "packing_tip": "O타입 어댑터, 강력한 자외선 차단제, 선글라스, 수영복",
        "must_visit": "시드니 오페라 하우스, 하버브리지, 본다이 비치, 블루블루"
    }
}

# 5. API 호출 함수 (캐싱)
@st.cache_data(ttl=600)
def get_weather(city_name, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric&lang=kr"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

@st.cache_data(ttl=3600)
def get_exchange_rates(api_key):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# 6. 상단 선택기 중앙 배치 및 크기 조절
col_space1, col_sel1, col_sel2, col_space2 = st.columns([0.8, 1.5, 1.5, 0.8])
with col_sel1:
    purpose = st.selectbox("🎯 사용 용도", ["여행용 🎒", "무역 실무용 💼"])
with col_sel2:
    selected_option = st.selectbox("✈️ 국가 및 도시", list(LOCATION_DATA.keys()))

target_city = LOCATION_DATA[selected_option]["city"]
target_currency = LOCATION_DATA[selected_option]["currency"]
currency_symbol = LOCATION_DATA[selected_option]["symbol"]
country_name = selected_option.split(' ')[0]

st.title(f"🌍 {country_name} 실시간 대시보드")
st.markdown("---")

col1, col2 = st.columns(2)

# ------------------ [좌측: 날씨 정보] ------------------
with col1:
    st.subheader(f"🌤️ {target_city.upper()} 날씨 정보")
    w_data = None
    if not WEATHER_API_KEY:
        st.error("날씨 API 키가 설정되지 않았습니다.")
    else:
        w_data = get_weather(target_city, WEATHER_API_KEY)
        if w_data:
            temp = w_data['main']['temp']
            feels_like = w_data['main']['feels_like']
            humidity = w_data['main']['humidity']
            wind_speed = w_data['wind']['speed']
            description = w_data['weather'][0]['description']
            icon_code = w_data['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
            
            st.markdown(f"**현재 날씨:** {temp:.1f}°C, {description}")
            st.image(icon_url, width=80)
            
            weather_html = f"""
<div class="info-card">
<div class="metric-container">
<div class="metric-box">
<div class="metric-value">{feels_like:.1f}°C</div>
<div class="metric-label">체감 온도</div>
</div>
<div class="metric-box">
<div class="metric-value">{humidity}%</div>
<div class="metric-label">습도</div>
</div>
<div class="metric-box">
<div class="metric-value">{wind_speed} m/s</div>
<div class="metric-label">풍속</div>
</div>
</div>
</div>
"""
            st.markdown(weather_html, unsafe_allow_html=True)
        else:
            st.error("날씨 정보를 불러오지 못했습니다.")

# ------------------ [우측: 환율 정보] ------------------
with col2:
    st.subheader(f"💱 {country_name} 환율 정보")
    target_to_krw = 0 
    e_data = None
    
    if not EXCHANGE_API_KEY:
        st.error("환율 API 키가 설정되지 않았습니다.")
    else:
        e_data = get_exchange_rates(EXCHANGE_API_KEY)
        if e_data and e_data.get("result") == "success":
            rates = e_data['conversion_rates']
            
            usd_to_krw = rates['KRW']
            target_to_krw = rates['KRW'] / rates[target_currency]
            
            display_rate = target_to_krw * 100 if target_currency == 'JPY' else target_to_krw
            display_unit = "100 JPY" if target_currency == 'JPY' else f"1 {target_currency}"
            
            st.markdown(f"**업데이트 기준일:** {e_data['time_last_update_utc'][:16]}")
            st.markdown("<div style='font-size: 65px; height: 80px; display: flex; align-items: center; margin-bottom: 1rem;'>💵</div>", unsafe_allow_html=True) 
            
            exchange_html = f"""
<div class="info-card">
<div class="metric-container">
<div class="metric-box">
<div class="metric-value">{display_rate:,.2f} 원</div>
<div class="metric-label">선택 국가 ({display_unit})</div>
</div>
<div class="metric-box">
<div class="metric-value">{usd_to_krw:,.2f} 원</div>
<div class="metric-label">기본 달러 (1 USD)</div>
</div>
</div>
</div>
"""
            st.markdown(exchange_html, unsafe_allow_html=True)

# ------------------ [맞춤형 정보 제공 (심층 분석)] ------------------
if w_data and e_data:
    st.markdown(f"### 📊 {purpose} 맞춤 심층 분석")
    
    compare_rate = display_rate
    base_rate = LOCATION_DATA[selected_option]['base_rate']
    
    if purpose == "여행용 🎒":
        weather_rec = "야외 활동을 하기에 쾌적하고 무난한 날씨입니다. 가벼운 발걸음으로 도시를 둘러보세요."
        if "비" in description or "눈" in description or "흐림" in description:
            weather_rec = "기상 상태가 좋지 않거나 비/눈 소식이 있습니다. 야외 일정보다는 박물관, 미술관, 대형 쇼핑몰 등 **실내 위주의 일정**을 강력히 추천합니다!"
        elif temp > 28:
            weather_rec = "기온이 높아 다소 덥습니다. 한낮에는 무리한 야외 활동을 피하시고, 충분한 수분 섭취와 그늘 휴식이 필수입니다."
        elif temp < 5:
            weather_rec = "날씨가 쌀쌀하거나 추우니 따뜻한 방한용품(목도리, 장갑, 패딩 등)을 꼭 챙기시고 실내 위주로 동선을 짜세요."
            
        if compare_rate > base_rate * 1.02:
            rate_rec = f"현재 환율({compare_rate:,.0f}원)이 기준선({base_rate}원)보다 높은 **원화 약세 구간**입니다. 현지 체류 시 예산이 초과되지 않도록 지출 관리에 조금 더 신경 쓰는 것이 좋습니다."
        elif compare_rate < base_rate * 0.98:
            rate_rec = f"현재 환율({compare_rate:,.0f}원)이 기준선({base_rate}원)보다 낮은 **원화 강세 구간**입니다. 환율 측면에서 매우 유리하므로 쇼핑이나 기념품 구매를 즐기기 딱 좋은 시기입니다!"
        else:
            rate_rec = f"현재 환율이 평년 수준을 안정적으로 유지하고 있어, 계획하셨던 여행 예산을 무리 없이 소화할 수 있습니다."

        st.markdown(f"""
        <div class="analysis-container">
            <div class="analysis-box" style="border-left-color: #3182CE;">
                <div class="analysis-title">🌤️ 실시간 날씨 맞춤 가이드</div>
                <div class="analysis-content">{weather_rec}</div>
            </div>
            <div class="analysis-box" style="border-left-color: #38A169;">
                <div class="analysis-title">💵 환율 현황 및 예산 팁</div>
                <div class="analysis-content">{rate_rec}</div>
            </div>
            <div class="analysis-box" style="border-left-color: #D69E2E;">
                <div class="analysis-title">🛒 현지 물가 및 필수 준비물</div>
                <div class="analysis-content">
                    <b>• 한국 대비 물가:</b> {LOCATION_DATA[selected_option]['price_level']}<br>
                    <b>• 추천 준비물:</b> {LOCATION_DATA[selected_option]['packing_tip']}
                </div>
            </div>
            <div class="analysis-box" style="border-left-color: #805AD5;">
                <div class="analysis-title">📍 현지 추천 핫플레이스</div>
                <div class="analysis-content">{LOCATION_DATA[selected_option]['must_visit']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    else: 
        if compare_rate > base_rate * 1.02:
            trade_rec = f"현재 환율({compare_rate:,.0f}원)이 기준선({base_rate}원)을 상회하는 <b>원화 약세장</b>입니다. <b>수출 기업</b>은 가격 경쟁력 확보 및 채산성 개선에 유리하며, <b>수입 기업</b>은 원가 부담이 커지므로 환헤지 및 계약 시점 조절이 필수적입니다."
        elif compare_rate < base_rate * 0.98:
            trade_rec = f"현재 환율({compare_rate:,.0f}원)이 기준선({base_rate}원)을 하회하는 <b>원화 강세장</b>입니다. <b>수입 기업</b>은 원자재나 부품 수입 단가를 낮추어 원가를 절감할 수 있으나, <b>수출 기업</b>은 가격 경쟁력 약화에 대비한 전략 점검이 필요합니다."
        else:
            trade_rec = "현재 환율이 안정적인 박스권 흐름을 보이고 있습니다. 환 리스크에 대한 부담이 적어 평소 기준에 맞춘 안정적인 대외 거래 진행이 가능합니다."

        st.markdown(f"""
        <div class="analysis-container">
            <div class="analysis-box" style="border-left-color: #E53E3E;">
                <div class="analysis-title">📈 실시간 환율 기반 수출입 전략</div>
                <div class="analysis-content">{trade_rec}</div>
            </div>
            <div class="analysis-box" style="border-left-color: #DD6B20;">
                <div class="analysis-title">💡 {country_name} 맞춤 무역 실무 및 비즈니스 팁</div>
                <div class="analysis-content">{LOCATION_DATA[selected_option]['trade_tip']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ------------------ [하단: 스위칭 환전 계산기] ------------------
st.markdown("---") 

if e_data and e_data.get("result") == "success":
    col_space1, col_center, col_space2 = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown(f"<h3 style='text-align: center;'>🧮 양방향 환전 계산기</h3>", unsafe_allow_html=True)
        
        calc_mode = st.radio("🔄 계산 방향 선택", [f"{target_currency} ➔ 원화(KRW)", f"원화(KRW) ➔ {target_currency}"], horizontal=True)
        
        if calc_mode.startswith(target_currency):
            input_amount = st.number_input(f"환전할 {country_name} 금액({target_currency})을 입력하세요:", min_value=0.0, value=100.0, step=10.0)
            krw_result = input_amount * target_to_krw
            st.success(f"예상 환전 금액: **{krw_result:,.0f} 원(KRW)**")
        else:
            input_amount = st.number_input(f"환전할 원화(KRW) 금액을 입력하세요:", min_value=0.0, value=100000.0, step=10000.0)
            target_result = input_amount / target_to_krw
            st.success(f"예상 환전 금액: **{currency_symbol} {target_result:,.2f}** ({target_currency})")