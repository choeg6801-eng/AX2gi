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

# 3. 커스텀 CSS
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #F4F9F4;
}
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
.stSelectbox div[data-baseweb="select"] {
    border-color: #FF7F50 !important;
    border-width: 2px !important;
    border-radius: 12px !important;
    min-height: 75px !important;
}
.stSelectbox div[data-baseweb="select"] span,
.stSelectbox div[data-baseweb="select"] div {
    font-size: 1.8rem !important;
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
.analysis-box {
    background-color: rgba(255, 255, 255, 0.95);
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    border-left: 6px solid #4A90E2;
    height: 100%;
}
.analysis-title {
    font-size: 1.1rem;
    font-weight: bold;
    color: #2C3E50;
    margin-bottom: 10px;
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

# 4. 지원 국가 데이터 (비자, 음식, 수출입, 경제 상황 상세 추가)
LOCATION_DATA = {
    "미국 (뉴욕)": {
        "city": "New York", "currency": "USD", "symbol": "$", 
        "base_rate": 1350, "price_level": "약 140% (주거 및 외식비 높음)", 
        "visa_free": "ESTA 사전 승인 시 최대 90일 체류 가능",
        "must_eat": "뉴욕 스타일 피자, 뉴욕 치즈케이크, 햄버거(셰이크셰이크)",
        "export_item": "자동차, 반도체, 항공기, 기계류, 화학공업제품",
        "import_item": "원유, 의약품, 컴퓨터, 통신기기, 채굴기",
        "biz_culture": "결론 우선주의(BLUNT 화법), 철저한 시간 준수, 계약서 기반의 비즈니스 진행",
        "econ_status": "견조한 소비 중심 성장세이나 고금리 장기화 및 상업용 부동산 리스크 상존",
        "packing_tip": "멀티탭(110V), 편한 운동화, 일교차 겉옷",
        "must_visit": "센트럴 파크, 타임스퀘어, 브로드웨이",
        "images": [
            "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1534430480872-3498386e7856?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "독일 (베를린)": {
        "city": "Berlin", "currency": "EUR", "symbol": "€", 
        "base_rate": 1450, "price_level": "약 110% (마트 물가는 저렴함)", 
        "visa_free": "무비자 관광 목적 최대 90일 체류 가능 (180일 기준)",
        "must_eat": "커리부르스트(Currywurst), 슈바인학센, 프레첼과 맥주",
        "export_item": "자동차 및 부품, 기계류, 화학제품, 전자의기",
        "import_item": "전기기기, 원유 및 천연가스, 자동차 부품, 컴퓨터",
        "biz_culture": "문서 증빙 및 규정 준수를 극도로 중시, 철저한 공사 구분, 격식 있는 호칭 사용",
        "econ_status": "제조업 부진 및 에너지 전환 비용 증가로 인해 완만한 성장 정체 국면",
        "packing_tip": "EU 어댑터, 방수 바람막이, 동전 지갑",
        "must_visit": "브란덴부르크 문, 베를린 장벽, 박물관 섬",
        "images": [
            "https://images.unsplash.com/photo-1560969184-10fe8719e047?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1599940824399-b87987ceb72a?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "일본 (도쿄)": {
        "city": "Tokyo", "currency": "JPY", "symbol": "¥", 
        "base_rate": 900, "price_level": "약 90% (엔저로 체감 물가 낮음)", 
        "visa_free": "관광 목적 무비자 최대 90일 체류 가능",
        "must_eat": "스시, 라멘, 몬쟈야끼, 톤카츠",
        "export_item": "자동차, 반도체 제조장비, 철강, 화학제품, 발전기",
        "import_item": "원유 및 액화천연가스(LNG), 의약품, 통신기기, 의류",
        "biz_culture": "신뢰 구축 중심의 장기적 관계 지향, 철저한 대면 비즈니스 예절(명함 교환 등)",
        "econ_status": "완만한 임금 인상과 완화적 통화정책 기조 속에서 점진적 경기 회복세",
        "packing_tip": "동전 지갑, 돼지코(110V), 숙소용 슬리퍼",
        "must_visit": "시부야 스크램블, 센소지, 도쿄타워",
        "images": [
            "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1536098561742-ca998e48cbcc?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "영국 (런던)": {
        "city": "London", "currency": "GBP", "symbol": "£", 
        "base_rate": 1700, "price_level": "약 145% (교통비/주거비 최고 수준)", 
        "visa_free": "무비자 관광 목적 최대 6개월 체류 가능",
        "must_eat": "피쉬 앤 칩스, 선데이 로스트, 애프터눈 티",
        "export_item": "기계류, 의약품, 자동차, 항공기 부품, 주류(위스키)",
        "import_item": "기계장치, 원유, 승용차, 의약품, 컴퓨터",
        "biz_culture": "간접적이고 예의 바른 우회적 화법, 스몰토크(날씨 등)로 미팅 시작",
        "econ_status": "브렉시트 이후 공급망 재편 및 고물가 여파로 완만한 회복 흐름",
        "packing_tip": "BF타입 어댑터, 튼튼한 3단 우산, 컨택리스 카드",
        "must_visit": "대영박물관, 런던 아이, 타워 브리지",
        "images": [
            "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1526129318478-62ed807ebdf9?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1506579309014-c3a444a35413?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "호주 (시드니)": {
        "city": "Sydney", "currency": "AUD", "symbol": "$", 
        "base_rate": 880, "price_level": "약 130% (외식/인건비 높음)", 
        "visa_free": "ETA(전자여행허가) 사전 승인 시 최대 3개월 체류 가능",
        "must_eat": "미트파이, 피쉬앤칩스(본다이 비치), 호주식 브런치와 플랫화이트",
        "export_item": "철광석, 석탄, LNG(천연가스), 금, 소고기 및 농축산물",
        "import_item": "정제유, 승용차, 화물자동차, 텔레콤 장비, 의약품",
        "biz_culture": "수평적이고 실용적인 분위기, 워라밸을 중시하며 빠른 의사결정 선호",
        "econ_status": "자원 수출 호조를 바탕으로 안정적 성장세를 보이나 주택 가격 및 가계 부채 부담 존재",
        "packing_tip": "O타입 어댑터, 자외선 차단제, 수영복",
        "must_visit": "오페라 하우스, 하버브리지, 본다이 비치",
        "images": [
            "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1523482580672-f109ba8cb9be?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=600&q=80"
        ]
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
col_space1, col_sel1, col_sel2, col_space2 = st.columns([2.0, 1.2, 1.2, 2.0])
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
            weather_rec = "기상 상태가 좋지 않거나 비/눈 소식이 있습니다. 야외 일정보다는 박물관, 미술관 등 **실내 위주의 일정**을 강력히 추천합니다!"
        elif temp > 28:
            weather_rec = "기온이 높아 다소 덥습니다. 한낮에는 무리한 야외 활동을 피하시고, 충분한 수분 섭취와 그늘 휴식이 필수입니다."
        elif temp < 5:
            weather_rec = "날씨가 쌀쌀하거나 추우니 따뜻한 방한용품을 꼭 챙기시고 실내 위주로 동선을 짜세요."
            
        if compare_rate > base_rate * 1.02:
            rate_rec = f"현재 환율({compare_rate:,.0f}원)이 기준선보다 높은 **원화 약세 구간**입니다. 현지 체류 시 예산 관리에 유의하세요."
        elif compare_rate < base_rate * 0.98:
            rate_rec = f"현재 환율({compare_rate:,.0f}원)이 기준선보다 낮은 **원화 강세 구간**입니다. 쇼핑과 기념품 구매를 즐기기 매우 좋은 시기입니다!"
        else:
            rate_rec = "현재 환율이 평년 수준을 유지하고 있어 계획하신 예산대로 안정적인 여행이 가능합니다."

        # 💡 여행용 4개 항목 (4등분 가로 나란히 배치)
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        
        with col_t1:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #3182CE;">
                <div class="analysis-title">🌤️ 날씨 가이드</div>
                <div class="analysis-content">{weather_rec}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_t2:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #38A169;">
                <div class="analysis-title">🛂 비자 및 체류 정보</div>
                <div class="analysis-content">
                    <b>• 체류 가능:</b> {LOCATION_DATA[selected_option]['visa_free']}<br><br>
                    <b>• 환율 팁:</b> {rate_rec}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_t3:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #D69E2E;">
                <div class="analysis-title">🍽️ 꼭 먹어야 할 음식</div>
                <div class="analysis-content">
                    <b>• 추천 메뉴:</b> {LOCATION_DATA[selected_option]['must_eat']}<br><br>
                    <b>• 현지 물가:</b> {LOCATION_DATA[selected_option]['price_level']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_t4:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #805AD5;">
                <div class="analysis-title">📍 필수 준비물 & 명소</div>
                <div class="analysis-content">
                    <b>• 준비물:</b> {LOCATION_DATA[selected_option]['packing_tip']}<br><br>
                    <b>• 핫플:</b> {LOCATION_DATA[selected_option]['must_visit']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # 핫플레이스 포토 갤러리 (3등분 가로 나란히)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"#### 📸 {country_name} 추천 핫플레이스 포토 갤러리")
        img_cols = st.columns(3)
        city_images = LOCATION_DATA[selected_option]["images"]
        
        for idx, col in enumerate(img_cols):
            with col:
                st.image(city_images[idx], use_container_width=True)
        
    else: # 무역 실무용 (4개 항목을 2x2 또는 4등분 배치하여 가독성 강화)
        if compare_rate > base_rate * 1.02:
            trade_rec = f"현재 환율({compare_rate:,.0f}원) 상회하는 **원화 약세장**: 수출 기업 유리, 수입 기업 원가 부담."
        elif compare_rate < base_rate * 0.98:
            trade_rec = f"현재 환율({compare_rate:,.0f}원) 하회하는 **원화 강세장**: 수입 기업 유리, 수출 기업 채산성 점검 필요."
        else:
            trade_rec = "현재 환율 안정세: 환 리스크 부담이 적어 안정적인 대외 거래 진행 가능."

        # 💡 무역 실무용 4개 항목을 4등분(st.columns(4))으로 가로 나란히 배치
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #E53E3E;">
                <div class="analysis-title">📦 주요 수출입품</div>
                <div class="analysis-content">
                    <b>• 수출:</b> {LOCATION_DATA[selected_option]['export_item']}<br><br>
                    <b>• 수입:</b> {LOCATION_DATA[selected_option]['import_item']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m2:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #DD6B20;">
                <div class="analysis-title">🤝 비즈니스 문화</div>
                <div class="analysis-content">{LOCATION_DATA[selected_option]['biz_culture']}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_m3:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #3182CE;">
                <div class="analysis-title">📊 경제 상황</div>
                <div class="analysis-content">{LOCATION_DATA[selected_option]['econ_status']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m4:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #38A169;">
                <div class="analysis-title">📈 환율 기반 전략</div>
                <div class="analysis-content">{trade_rec}</div>
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