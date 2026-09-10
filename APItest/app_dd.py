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

# 3. 커스텀 CSS (목록바 글자 크기 대폭 확대 및 자몽색 테두리)
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

/* 셀렉트박스 글자 크기를 더 크게 키우고 박스 높이 조정 */
.stSelectbox div[data-baseweb="select"] {
    border-color: #FF7F50 !important; /* 자몽색 테두리 */
    border-width: 2px !important;
    border-radius: 12px !important;
    min-height: 75px !important;
}
.stSelectbox div[data-baseweb="select"] span,
.stSelectbox div[data-baseweb="select"] div {
    font-size: 1.8rem !important; /* 글자 크기 대폭 확대 */
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

# 4. 💡 스페인 및 남미 국가(브라질, 아르헨티나) 추가 완료된 전체 국가 데이터
LOCATION_DATA = {
    "미국 (뉴욕)": {
        "city": "New York", "currency": "USD", "symbol": "$", 
        "base_rate": 1350, "price_level": "약 140% (주거 및 외식비 높음)", 
        "trade_export": "자동차, 반도체, 기계류, 석유제품",
        "trade_import": "원유, 천연가스, 항공기, 농산물",
        "trade_culture": "결론 우선 직설적 화법 선호, 계약서 상의 문서 증빙과 준법 정신을 극도로 중시",
        "trade_economy": "견조한 소비 중심 성장이나 고금리 장기화로 인한 자금 조달 비용 부담 존재",
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
        "trade_export": "자동차부품, 배터리, 화학제품, 기계",
        "trade_import": "천연가스, 의약품, 전자제품, 원유",
        "trade_culture": "엄격한 규정과 절차 준수, 공사 구분 명확, 철저한 사전 서면 검토 요구",
        "trade_economy": "제조업 부진 및 에너지 전환 비용 증가로 인해 완만한 성장 정체 국면",
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
        "trade_export": "철강, 반도체 장비, 전자부품, 자동차",
        "trade_import": "액화천연가스(LNG), 원유, 의류, 식료품",
        "trade_culture": "격식 있는 호칭과 철저한 비즈니스 예절(명함 교환 등), 신뢰 구축 중시",
        "trade_economy": "완만한 임금 상승과 관광객 유입으로 내수 회복세이나 엔화 변동성 주의",
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
        "trade_export": "승용차, 의약품, 바이오, 기계류",
        "trade_import": "원유, 천연가스, 기계장치, 귀금속",
        "trade_culture": "우회적이고 정중한 화법 사용, 비즈니스 네트워킹과 신용도 매우 중시",
        "trade_economy": "서비스 산업 중심의 경제이나 고금리 및 브렉시트 여파로 성장 둔화 압력",
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
        "trade_export": "석유제품, 자동차, 기계, 정밀기기",
        "trade_import": "철광석, 석탄, 천연가스, 여행·교육 서비스",
        "trade_culture": "워라밸을 중시하며 수평적이고 실용적인 커뮤니케이션 선호",
        "trade_economy": "자원 수출 호조를 보이고 있으나 높은 인플레이션과 금리 압박 존재",
        "packing_tip": "O타입 어댑터, 자외선 차단제, 수영복",
        "must_visit": "오페라 하우스, 하버브리지, 본다이 비치",
        "images": [
            "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1523482580672-f109ba8cb9be?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "스페인 (마드리드)": {
        "city": "Madrid", "currency": "EUR", "symbol": "€", 
        "base_rate": 1450, "price_level": "약 85% (서유럽 대비 물가와 식료품비가 저렴함)", 
        "trade_export": "자동차, 기계류, 의류(패션), 올리브유",
        "trade_import": "원유, 천연가스, 의약품, 전자부품",
        "trade_culture": "대면 소통과 인간관계(인맥)를 중요시하며, 격식보다는 친근하고 유연한 태도를 선호",
        "trade_economy": "관광업 호조 및 신재생 에너지 투자 확대로 완만한 성장세를 보이나 청년 실업률 다소 높음",
        "packing_tip": "유럽용 멀티어댑터, 선글라스, 가벼운 옷차림",
        "must_visit": "프라도 미술관, 마요르 광장, 레티로 공원",
        "images": [
            "https://images.unsplash.com/photo-1539037116277-4db20889f2d4?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1543785734-4b6e564642f8?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1509114397022-ed747cca3f65?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "브라질 (상파울루)": {
        "city": "Sao Paulo", "currency": "BRL", "symbol": "R$", 
        "base_rate": 270, "price_level": "약 75% (공산품은 비싸지만 현지 식품 물가는 저렴함)", 
        "trade_export": "철강, 자동차 부품, 화학제품, 전자제품",
        "trade_import": "대두, 철광석, 원유, 육류(소고기/가금류), 커피",
        "trade_culture": "따뜻하고 정중한 인사와 악수를 중시하며, 서두르지 않는 여유로운 비즈니스 스타일",
        "trade_economy": "자원 및 농축산물 수출 대국이나 높은 인플레이션과 환율 변동성에 주의 필요",
        "packing_tip": "변압기(대부분 110V/220V 혼용이나 확인 필요), 소매치기 방지 백팩, 모기 기피제",
        "must_visit": "파울리스타 대로, 이비라푸에라 공장, 상파울루 미술관",
        "images": [
            "https://images.unsplash.com/photo-1531737704602-44287528e1a1?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1483729558449-99ef09a8c325?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1512813266185-3b1f5fc23015?auto=format&fit=crop&w=600&q=80"
        ]
    },
    "아르헨티나 (부에노스아이레스)": {
        "city": "Buenos Aires", "currency": "ARS", "symbol": "$", 
        "base_rate": 1.5, "price_level": "약 60% (외국인 환율 체감상 물가가 매우 저렴하게 느껴짐)", 
        "trade_export": "기계류, 자동차 부품, 화학제품, 플라스틱",
        "trade_import": "곡물(대두/밀), 육류, 리튬, 원유 및 가스",
        "trade_culture": "친근한 스킨십(볼 키스 등)과 대화를 선호하며, 개인적인 유대감을 쌓은 뒤 거래 진행",
        "trade_economy": "만성적인 고인플레이션과 복잡한 외환 규제가 존재하므로 대금 결제 조건 리스크 관리 필수",
        "packing_tip": "C/I 타입 겸용 어댑터, 넉넉한 현금(달러 선호), 편한 산책화",
        "must_visit": "라보카(캄니토), 5월 광장, 오벨리스크",
        "images": [
            "https://images.unsplash.com/photo-1589909202874-17f975762af0?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1612294037637-ec32374e2846?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1583321500900-82807e45c03e?auto=format&fit=crop&w=600&q=80"
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

# ------------------ [맞춤형 정보 제공 (4분할 가로 나란히 배치)] ------------------
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
                <div class="analysis-title">💵 환율 예산 팁</div>
                <div class="analysis-content">{rate_rec}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_t3:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #D69E2E;">
                <div class="analysis-title">🛒 물가 및 준비물</div>
                <div class="analysis-content">
                    <b>• 물가:</b> {LOCATION_DATA[selected_option]['price_level']}<br><br>
                    <b>• 준비물:</b> {LOCATION_DATA[selected_option]['packing_tip']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_t4:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #805AD5;">
                <div class="analysis-title">📍 추천 핫플레이스</div>
                <div class="analysis-content">{LOCATION_DATA[selected_option]['must_visit']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"#### 📸 {country_name} 추천 핫플레이스 포토 갤러리")
        img_cols = st.columns(3)
        city_images = LOCATION_DATA[selected_option]["images"]
        
        for idx, col in enumerate(img_cols):
            with col:
                st.image(city_images[idx], use_container_width=True)
        
    else: # 무역 실무용 (수출/수입 분리 4분할 가로 나란히 배치)
        if compare_rate > base_rate * 1.02:
            trade_rec = f"현재 환율({compare_rate:,.0f}원) 상회하는 <b>원화 약세장</b>: <b>수출 기업</b> 가격 경쟁력 확보 유리, <b>수입 기업</b> 원가 부담 증가로 환헤지 필수."
        elif compare_rate < base_rate * 0.98:
            trade_rec = f"현재 환율({compare_rate:,.0f}원) 하회하는 <b>원화 강세장</b>: <b>수입 기업</b> 원자재 단가 절감 유리, <b>수출 기업</b> 채산성 악화 대비 전략 필요."
        else:
            trade_rec = "현재 환율이 안정적인 박스권을 보이며 환 리스크 부담이 적어 평소 기준에 맞춘 안정적인 대외 거래가 가능합니다."

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #DD6B20;">
                <div class="analysis-title">📤 주요 수출품</div>
                <div class="analysis-content">{LOCATION_DATA[selected_option]['trade_export']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m2:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #3182CE;">
                <div class="analysis-title">📥 주요 수입품</div>
                <div class="analysis-content">{LOCATION_DATA[selected_option]['trade_import']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m3:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #D69E2E;">
                <div class="analysis-title">🤝 비즈니스 문화</div>
                <div class="analysis-content">{LOCATION_DATA[selected_option]['trade_culture']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m4:
            st.markdown(f"""
            <div class="analysis-box" style="border-left-color: #E53E3E;">
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