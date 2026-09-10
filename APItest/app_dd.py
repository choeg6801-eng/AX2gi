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

# 3. 커스텀 CSS (배경에 세계지도 이미지 및 50% 투명도 적용)
st.markdown("""
<style>
/* 💡 파스텔 배경을 지우고 투명도 50%의 세계지도 배경을 적용합니다 */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.5)), 
                url("https://upload.wikimedia.org/wikipedia/commons/8/80/World_map_-_low_resolution.svg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
[data-testid="stHeader"] {
    background-color: rgba(0,0,0,0);
}
.info-card {
    background-color: rgba(248, 249, 250, 0.9); /* 카드가 지도 위에서 잘 보이도록 살짝 불투명도 조절 */
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 20px;
    height: 100%;
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
.custom-box {
    background-color: rgba(255, 255, 255, 0.95);
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    margin-top: 15px;
    border-left: 5px solid #4A90E2;
}
</style>
""", unsafe_allow_html=True)

# 4. 지원 국가 데이터 (물가, 기준 환율, 무역 팁 포함)
LOCATION_DATA = {
    "미국 (뉴욕)": {
        "city": "New York", "currency": "USD", "symbol": "$", 
        "base_rate": 1350, "price_level": "약 140% (주거 및 외식비가 매우 높음)", 
        "trade_tip": "주요 수출품: 자동차, 기계류. 통상 압박(IRA 등) 모니터링 필수. 비즈니스 미팅 시 결론부터 말하는 직설적인 화법을 선호합니다."
    },
    "독일 (베를린)": {
        "city": "Berlin", "currency": "EUR", "symbol": "€", 
        "base_rate": 1450, "price_level": "약 110% (마트 장바구니 물가는 저렴하나, 서비스 요금이 높음)", 
        "trade_tip": "주요 수출품: 배터리, 화학제품. CE 인증 등 환경/안전 규제가 매우 엄격합니다. 구두 약속보다 계약서와 문서 증빙을 극도로 중시합니다."
    },
    "일본 (도쿄)": {
        "city": "Tokyo", "currency": "JPY", "symbol": "¥", 
        "base_rate": 900, "price_level": "약 90% (최근 엔저 현상으로 체감 물가가 한국보다 낮음)", 
        "trade_tip": "주요 수출품: 철강, 전자부품. 품질 기준이 까다로우며 신뢰 구축에 오랜 시간이 걸립니다. 대면 미팅과 비즈니스 예절(명함 교환 등)이 매우 중요합니다."
    },
    "영국 (런던)": {
        "city": "London", "currency": "GBP", "symbol": "£", 
        "base_rate": 1700, "price_level": "약 145% (교통비와 런던 내 주거비가 세계 최고 수준)", 
        "trade_tip": "주요 수출품: 승용차, 바이오. 브렉시트(Brexit) 이후 독자적인 영국 인증(UKCA)을 도입했습니다. 간접적이고 우회적인 화법에 주의해야 합니다."
    },
    "호주 (시드니)": {
        "city": "Sydney", "currency": "AUD", "symbol": "$", 
        "base_rate": 880, "price_level": "약 130% (외식비, 인건비가 높아 전반적인 서비스 물가 높음)", 
        "trade_tip": "주요 수출품: 석유제품, 자동차. 자원 강국이므로 원자재 수입 비중이 높습니다. 검역(목재, 식품 등)이 세계 최고 수준으로 까다로우니 주의하세요."
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

# 6. 상단 선택기 (비율 1.5 : 1.5 : 3)
col_sel1, col_sel2, col_blank = st.columns([1.5, 1.5, 3])
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

# ------------------ [맞춤형 정보 제공 (AI 분석)] ------------------
if w_data and e_data:
    st.markdown(f"### {purpose.split(' ')[0]} 맞춤 정보 분석")
    
    compare_rate = display_rate
    base_rate = LOCATION_DATA[selected_option]['base_rate']
    
    if purpose == "여행용 🎒":
        weather_rec = "도보 여행 및 시티투어 등 야외 활동을 하기에 무난한 날씨입니다."
        if "비" in description or "눈" in description or "흐림" in description:
            weather_rec = "비나 눈이 올 수 있습니다. 미술관, 박물관, 쇼핑몰 등 쾌적한 **실내 랜드마크 위주의 일정**을 추천합니다. 우산 챙기기를 잊지 마세요!"
        elif temp > 28:
            weather_rec = "날씨가 다소 덥습니다. 한낮에는 야외 활동을 피하고, 시원한 실내 코스나 수영장, 워터파크 등의 일정을 추천합니다."
        elif temp < 5:
            weather_rec = "날씨가 춥습니다. 따뜻한 외투가 필수이며, 무리한 야외 이동보다는 따뜻한 카페나 온천, 실내 관람 위주로 계획하세요."
            
        if compare_rate > base_rate * 1.02:
            rate_rec = f"현재 환율({compare_rate:,.0f}원)이 평균({base_rate}원)보다 **높은 편(원화 약세)**입니다. 쇼핑이나 외식 등 현지 지출 시 예산이 초과되지 않도록 유의하세요."
        elif compare_rate < base_rate * 0.98:
            rate_rec = f"현재 환율({compare_rate:,.0f}원)이 평균({base_rate}원)보다 **낮은 편(원화 강세)**입니다. 상대적으로 저렴하게 여행과 쇼핑을 즐기기 좋은 시기입니다!"
        else:
            rate_rec = f"현재 환율은 평균 수준을 유지하고 있어, 계획하신 예산대로 안정적인 여행이 가능합니다."

        st.markdown(f"""
        <div class="custom-box">
            <b>🌤️ 오늘의 날씨 팁:</b> {weather_rec}<br><br>
            <b>💵 환율 기반 추천도:</b> {rate_rec}<br><br>
            <b>🛒 한국(서울) 대비 물가:</b> {LOCATION_DATA[selected_option]['price_level']}
        </div>
        """, unsafe_allow_html=True)
        
    else: 
        if compare_rate > base_rate * 1.02:
            trade_rec = f"현재 환율({compare_rate:,.0f}원)이 기준선({base_rate}원)을 상회하는 **원화 약세장**입니다. <b>수출 기업</b>은 가격 경쟁력을 확보하고 마진을 남기기 유리합니다. 반면 <b>수입 기업</b>은 원자재 단가 인상 압박이 있으므로 수입 물량 조절이 필요합니다."
        elif compare_rate < base_rate * 0.98:
            trade_rec = f"현재 환율({compare_rate:,.0f}원)이 기준선({base_rate}원)을 하회하는 **원화 강세장**입니다. <b>수입 기업</b>은 원자재나 부품 수입 단가를 낮출 수 있어 유리합니다. 반면 <b>수출 기업</b>은 채산성 악화 우려가 있으므로 환헤지 전략을 점검하세요."
        else:
            trade_rec = "현재 환율이 기준선 부근에서 안정적인 흐름을 보이고 있습니다. 환 리스크가 비교적 적어 정상적인 결제 및 무역 거래 진행에 무리가 없습니다."

        st.markdown(f"""
        <div class="custom-box">
            <b>📈 실시간 환율 기반 거래 가이드:</b><br>{trade_rec}<br><br>
            <b>💡 {country_name} 무역 실무 및 비즈니스 팁:</b><br>{LOCATION_DATA[selected_option]['trade_tip']}
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