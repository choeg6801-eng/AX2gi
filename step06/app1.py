import os
from pathlib import Path
import streamlit as st
import requests
from dotenv import load_dotenv
import folium
from streamlit_folium import st_folium

# 페이지 설정 (와이드 레이아웃)
st.set_page_config(
    page_title="여행 감성 주변 장소 탐색",
    page_icon="🗺️",
    layout="wide"
)

# 🎨 커스텀 CSS 적용 (카드 UI 및 전체적인 디자인 감성 업그레이드)
st.markdown("""
    <style>
    .main {
        background-color: #faf9f6;
    }
    .app-title {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #2d3436;
    }
    </style>
""", unsafe_allow_html=True)

# 메인 타이틀 & 안내 문구
st.markdown("<h2 class='app-title'>🗺️ 나의 감성 여행 지도 스폿</h2>", unsafe_allow_html=True)
st.markdown("✨ 가고 싶은 장소를 쏙쏙 골라보고, 지도로 한눈에 확인해보세요.")
st.divider()

# 📌 .env 파일 상위 폴더 경로 탐색 및 로드
current_dir = Path(__file__).resolve().parent
env_path = current_dir.parent / '.env'

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    alt_env_path = current_dir / '.env'
    if alt_env_path.exists():
        load_dotenv(dotenv_path=alt_env_path)
        env_path = alt_env_path

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

# API 키 확인 및 상세 안내
if not KAKAO_REST_API_KEY:
    st.error(f"⚠️ 환경 변수를 불러오지 못했습니다.")
    st.info(f"확인된 탐색 경로: `{env_path}`\n\n상위 폴더에 `.env` 파일이 정상적으로 위치해 있는지, 파일 내부에 `KAKAO_REST_API_KEY=your_key` 형태로 작성되어 있는지 확인해주세요.")
    st.stop()

# 기준 위치 설정 (기본값: 서울시청)
DEFAULT_LAT = 37.566535  
DEFAULT_LNG = 126.977969 

# 사이드바 디자인
with st.sidebar:
    st.markdown("### 🧭 탐색 설정")
    user_lat = st.number_input("기준 위도", value=DEFAULT_LAT, format="%.6f")
    user_lng = st.number_input("기준 경도", value=DEFAULT_LNG, format="%.6f")
    st.caption("여행 중심이 될 좌표를 설정하세요.")

    st.markdown("---")
    st.markdown("### 🏷️ 카테고리 테마")
    
    category_options = {
        "직접 입력하기": "",
        "🍽️ 맛있는 미식 탐방": "FD6",
        "☕ 감성 카페 투어": "CE7",
        "🏪 편의점": "CS2",
        "🛒 대형마트": "MT1",
        "🏫 학교": "SC4",
        "학원": "AC5",
        "🏨 숙박·스테이": "AD5",
        " 은행": "BK9",
        " 병원": "HP8",
        " 약국": "PM9",
        " 지하철역": "SW8",
        " 주유소/충전소": "OL7",
        "🅿️ 주차장": "PK6",
        " 문화시설": "CT1",
        " 관광명소": "AT4",
        " 공공기관": "PO3",
        " 반려동물 동반/시설": "AN7"
    }
    
    selected_category_name = st.selectbox("어떤 장소를 찾고 계신가요?", list(category_options.keys()), key="cat_select")
    selected_category_code = category_options[selected_category_name]

# 검색어 입력 로직
if selected_category_code == "":
    query = st.text_input("검색하고 싶은 키워드를 입력하세요", placeholder="예: 한강공원, 소품샵 등")
else:
    category_clean_name = selected_category_name.split()[-1] if len(selected_category_name.split()) > 1 else selected_category_name
    sub_query = st.text_input(f"[{category_clean_name}] 상세 검색어 (선택 사항)", placeholder="비워두면 주변 전체를 보여드려요")
    query = sub_query if sub_query else category_clean_name

# 검색 상태 초기화 관리
if "last_query_key" not in st.session_state:
    st.session_state.last_query_key = ""
if "selected_idx" not in st.session_state:
    st.session_state.selected_idx = 0

current_search_key = f"{selected_category_code}_{query}"

if current_search_key != st.session_state.last_query_key:
    st.session_state.last_query_key = current_search_key
    st.session_state.selected_idx = 0
    if query.strip() != "" or selected_category_code != "":
        st.rerun()

if query.strip() != "" or selected_category_code != "":
    if selected_category_code:
        url = "https://dapi.kakao.com/v2/local/search/category.json"
        params = {
            "category_group_code": selected_category_code,
            "x": str(user_lng),
            "y": str(user_lat),
            "radius": 10000,
            "sort": "distance"
        }
        if sub_query:
            params["query"] = sub_query
    else:
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        params = {
            "query": query,
            "x": str(user_lng),
            "y": str(user_lat),
            "radius": 10000,
            "sort": "distance"
        }

    headers = {
        "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"
    }

    with st.spinner("✨ 반짝이는 장소들을 불러오는 중이에요..."):
        response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        documents = data.get("documents", [])

        if documents:
            st.success(f"🎉 반경 10km 내에서 매력적인 장소 **{len(documents)}개**를 찾았어요!")

            col1, col2 = st.columns([1, 1.4], gap="medium")

            with col1:
                st.markdown("#### 📋 추천 스폿 리스트")
                st.caption("버튼을 탭하면 지도가 해당 장소를 다정하게 비춰줍니다.")

                for idx, place in enumerate(documents):
                    place_name = place["place_name"]
                    address = place["road_address_name"] or place["address_name"]
                    phone = place.get("phone", "번호 없음")
                    place_url = place.get("place_url", "#")
                    
                    distance_meters = float(place.get("distance", 0))
                    distance_km = distance_meters / 1000

                    is_selected = (st.session_state.selected_idx == idx)
                    button_label = f"📍 {idx+1}. {place_name} ({distance_km:.2f} km)"
                    
                    if st.button(button_label, key=f"btn_{idx}", use_container_width=True, type="primary" if is_selected else "secondary"):
                        st.session_state.selected_idx = idx
                        st.rerun()

                    st.markdown(f"<span style='color:#636e72; font-size:14px;'>🏠 {address}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color:#636e72; font-size:14px;'>🚗 기준 위치로부터 {distance_km:.2f} km</span>", unsafe_allow_html=True)
                    if phone != "번호 없음":
                        st.markdown(f"<span style='color:#636e72; font-size:14px;'>☎️ {phone}</span>", unsafe_allow_html=True)
                    
                    st.markdown(f"🔗 [카카오맵 상세 정보 보기]({place_url})", unsafe_allow_html=True)
                    st.markdown("---")

            with col2:
                st.markdown("#### 🗺️ 위치 한눈에 보기")

                current_idx = st.session_state.selected_idx
                if current_idx >= len(documents):
                    current_idx = 0

                selected_place = documents[current_idx]
                center_lat = float(selected_place["y"])
                center_lng = float(selected_place["x"])

                # 💡 API 오류 방지를 위해 기본 지도 타일(OpenStreetMap) 사용
                m = folium.Map(location=[center_lat, center_lng], zoom_start=17)

                # 1. 기준 위치 마커
                folium.Marker(
                    location=[user_lat, user_lng],
                    popup=folium.Popup("<b>여행 시작점</b>", max_width=200),
                    tooltip="🏠 기준 위치",
                    icon=folium.Icon(color="orange", icon="home", prefix="fa")
                ).add_to(m)

                # 2. 반경 10km 감성 원 표시
                folium.Circle(
                    location=[user_lat, user_lng],
                    radius=10000,
                    color="#ff7675",
                    fill=True,
                    fill_color="#ff7675",
                    fill_opacity=0.04,
                    tooltip="탐색 반경 10km"
                ).add_to(m)

                # 3. 검색된 장소 마커들
                for idx, place in enumerate(documents):
                    lat = float(place["y"])
                    lng = float(place["x"])
                    place_name = place["place_name"]
                    address = place["road_address_name"] or place["address_name"]
                    distance_km = float(place.get("distance", 0)) / 1000
                    place_url = place.get("place_url", "#")

                    if idx == current_idx:
                        icon = folium.Icon(color="red", icon="heart", prefix="fa")
                        tooltip_prefix = "💖 [선택된 스폿] "
                    else:
                        icon = folium.Icon(color="blue", icon="map-pin", prefix="fa")
                        tooltip_prefix = f"{idx+1}. "

                    popup_html = f"""
                    <div style="width:210px; font-family:sans-serif;">
                      <b style="font-size:15px; color:#2d3436;">{place_name}</b><br>
                      <span style="font-size:12px; color:#636e72;">{address}</span><br>
                      <span style="font-size:12px; color:#0984e3;">거리: {distance_km:.2f}km</span><br>
                      <a href="{place_url}" target="_blank" style="font-size:12px; text-decoration:none; color:#e17055;">카카오맵에서 열기 ➔</a>
                    </div>
                    """

                    folium.Marker(
                        location=[lat, lng],
                        popup=folium.Popup(popup_html, max_width=250),
                        tooltip=f"{tooltip_prefix}{place_name} ({distance_km:.2f}km)",
                        icon=icon
                    ).add_to(m)

                st_folium(m, width=720, height=580)

        else:
            st.warning("앗, 설정하신 조건에 딱 맞는 장소를 찾지 못했어요. 검색어나 카테고리를 살짝 바꿔볼까요?")
    else:
        st.error(f"데이터를 불러오는 중 문제가 발생했어요. (코드: {response.status_code})")
        st.json(response.json())