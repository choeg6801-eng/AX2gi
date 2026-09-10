import os
import requests
import streamlit as st
from dotenv import load_dotenv

# 1. 환경 변수 로드 (.env 파일에서 API 키 가져오기)
load_dotenv() 
WEATHER_API_KEY = os.getenv("openweather_API_key")
EXCHANGE_API_KEY = os.getenv("exchange_API_key") # 환율 API 키 추가

# 2. Streamlit 페이지 설정 (화면을 넓게 쓰기 위해 layout="wide"로 변경)
st.set_page_config(page_title="날씨 & 환율 대시보드", page_icon="🌍", layout="wide")

# 3. 커스텀 CSS (반응형 디자인 및 카드 UI 스타일링)
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

# 4. 앱 상단 UI
st.title("🌍 실시간 날씨 및 환율 대시보드")
st.write("도시 이름을 입력하여 현재 날씨와 주요 통화의 환율(원화 기준)을 동시에 확인하세요.")

city_name = st.text_input("도시 이름 입력 (영어)", "Seoul")

# 버튼 클릭 시 실행
if st.button("정보 조회하기"):
    # 화면을 좌우 2개의 컬럼으로 분할
    col1, col2 = st.columns(2)
    
    # ------------------ [좌측: 날씨 정보] ------------------
    with col1:
        st.subheader("🌤️ 날씨 정보")
        if not WEATHER_API_KEY:
            st.error("날씨 API 키가 설정되지 않았습니다.")
        elif city_name:
            weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric&lang=kr"
            try:
                w_response = requests.get(weather_url)
                w_data = w_response.json()
                
                if w_response.status_code == 200:
                    temp = w_data['main']['temp']
                    feels_like = w_data['main']['feels_like']
                    humidity = w_data['main']['humidity']
                    wind_speed = w_data['wind']['speed']
                    description = w_data['weather'][0]['description']
                    icon_code = w_data['weather'][0]['icon']
                    icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
                    
                    st.markdown(f"**{city_name.upper()}**의 현재 날씨: {temp:.1f}°C, {description}")
                    st.image(icon_url, width=80)
                    
                    # 날씨 HTML 렌더링 (들여쓰기 제거 필수)
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
                    st.error(f"날씨 정보를 가져올 수 없습니다. (에러: {w_response.status_code})")
            except Exception as e:
                st.error(f"날씨 조회 오류: {e}")

    # ------------------ [우측: 환율 정보] ------------------
    with col2:
        st.subheader("💱 주요 통화 환율 (KRW)")
        if not EXCHANGE_API_KEY:
            st.error("환율 API 키가 설정되지 않았습니다.")
        else:
            # 환율 API 호출 (USD 기준)
            exchange_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/USD"
            try:
                e_response = requests.get(exchange_url)
                e_data = e_response.json()
                
                if e_response.status_code == 200 and e_data.get("result") == "success":
                    rates = e_data['conversion_rates']
                    # 환율 계산 (USD, EUR, JPY -> KRW)
                    # JPY는 100엔당 원화로 표시하는 것이 일반적이므로 * 100을 해줍니다.
                    usd_to_krw = rates['KRW']
                    eur_to_krw = rates['KRW'] / rates['EUR']
                    jpy_to_krw = (rates['KRW'] / rates['JPY']) * 100
                    
                    st.markdown(f"**업데이트 기준일:** {e_data['time_last_update_utc'][:16]}")
# 왼쪽 날씨 아이콘 높이에 맞춰 85px의 투명한 여백을 만듭니다.
                    st.markdown("<div style='height: 85px;'></div>", unsafe_allow_html=True)
                    
                    # 환율 HTML 렌더링 (들여쓰기 제거 필수)
                    exchange_html = f"""
<div class="info-card">
<div class="metric-container">
<div class="metric-box">
<div class="metric-value">{usd_to_krw:,.2f} 원</div>
<div class="metric-label">미국 달러 (1 USD)</div>
</div>
<div class="metric-box">
<div class="metric-value">{eur_to_krw:,.2f} 원</div>
<div class="metric-label">유로 (1 EUR)</div>
</div>
<div class="metric-box">
<div class="metric-value">{jpy_to_krw:,.2f} 원</div>
<div class="metric-label">일본 엔 (100 JPY)</div>
</div>
</div>
</div>
"""
                    st.markdown(exchange_html, unsafe_allow_html=True)
                else:
                    st.error(f"환율 정보를 가져올 수 없습니다. API 키를 확인해주세요.")
            except Exception as e:
                st.error(f"환율 조회 오류: {e}")