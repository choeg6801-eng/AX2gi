import os
import requests
import streamlit as st
from dotenv import load_dotenv

# 1. 환경 변수 로드
load_dotenv() 
WEATHER_API_KEY = os.getenv("openweather_API_key")
EXCHANGE_API_KEY = os.getenv("exchange_API_key")

# 2. 페이지 설정
st.set_page_config(page_title="글로벌 날씨 & 환율 대시보드", page_icon="🌍", layout="wide")

# 3. 커스텀 CSS (들여쓰기 없음)
st.markdown("""
<style>
.info-card {
background-color: #f8f9fa;
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
</style>
""", unsafe_allow_html=True)

# 4. 지원할 국가 및 도시, 통화 데이터 맵핑
LOCATION_DATA = {
    "미국 (뉴욕)": {"city": "New York", "currency": "USD", "symbol": "$"},
    "독일 (베를린)": {"city": "Berlin", "currency": "EUR", "symbol": "€"},
    "대한민국 (서울)": {"city": "Seoul", "currency": "KRW", "symbol": "₩"},
    "일본 (도쿄)": {"city": "Tokyo", "currency": "JPY", "symbol": "¥"},
    "영국 (런던)": {"city": "London", "currency": "GBP", "symbol": "£"},
    "호주 (시드니)": {"city": "Sydney", "currency": "AUD", "symbol": "$"}
}

# 5. API 호출 함수 (캐싱 적용: API 무료 호출 횟수 보호)
@st.cache_data(ttl=600) # 날씨는 10분(600초) 동안 데이터 기억
def get_weather(city_name, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric&lang=kr"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

@st.cache_data(ttl=3600) # 환율은 1시간(3600초) 동안 데이터 기억
def get_exchange_rates(api_key):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# 6. 앱 UI 구성
# 상단: 국가 선택
selected_option = st.selectbox("✈️ 조회할 국가 및 도시를 선택하세요:", list(LOCATION_DATA.keys()))
target_city = LOCATION_DATA[selected_option]["city"]
target_currency = LOCATION_DATA[selected_option]["currency"]
currency_symbol = LOCATION_DATA[selected_option]["symbol"]

# 타이틀 동적 변경
st.title(f"🌍 {selected_option.split(' ')[0]} 실시간 대시보드")
st.markdown("---")

# 레이아웃 분할
col1, col2 = st.columns(2)

# ------------------ [좌측: 날씨 정보] ------------------
with col1:
    st.subheader(f"🌤️ {target_city.upper()} 날씨 정보")
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

# ------------------ [우측: 환율 및 계산기] ------------------
with col2:
    st.subheader(f"💱 환율 정보 & 환전 계산기")
    if not EXCHANGE_API_KEY:
        st.error("환율 API 키가 설정되지 않았습니다.")
    else:
        e_data = get_exchange_rates(EXCHANGE_API_KEY)
        if e_data and e_data.get("result") == "success":
            rates = e_data['conversion_rates']
            
            # 환율 계산 (목표 통화 1단위 당 원화 가격)
            usd_to_krw = rates['KRW']
            target_to_krw = rates['KRW'] if target_currency == 'KRW' else (rates['KRW'] / rates[target_currency])
            
            # JPY(엔화)의 경우 통상적으로 100엔 단위로 표기
            display_rate = target_to_krw * 100 if target_currency == 'JPY' else target_to_krw
            display_unit = "100 JPY" if target_currency == 'JPY' else f"1 {target_currency}"
            
            st.markdown(f"**업데이트 기준일:** {e_data['time_last_update_utc'][:16]}")
            st.markdown("<div style='height: 85px;'></div>", unsafe_allow_html=True) 
            
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
            
            # --- 환전 계산기 구현 ---
            st.markdown("### 🧮 원화 환전 계산기")
            krw_input = st.number_input("환전할 원화(KRW) 금액을 입력하세요:", min_value=0, value=100000, step=10000)
            
            if target_currency == "KRW":
                exchanged_amount = krw_input
            else:
                exchanged_amount = krw_input / target_to_krw
                
            st.success(f"예상 환전 금액: **{currency_symbol} {exchanged_amount:,.2f}** ({target_currency})")
            
        else:
            st.error("환율 정보를 불러오지 못했습니다.")