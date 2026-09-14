import os
from pathlib import Path
import streamlit as st
import requests
from dotenv import load_dotenv  # 'load-dotenv'를 'load_dotenv'로 수정
import folium
from streamlit_folium import st_folium

# 상위 폴더에 있는 .env 파일 경로 지정하여 로드
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

# 페이지 설정
st.set_page_config(
    page_title="카카오 지도 장소 검색",
    page_icon="📍",
    layout="wide"
)

# 제목 및 안내 메시지
st.markdown("### 📍 카테고리별 맞춤 주변 장소 검색 (반경 10km / 거리순)")
st.info("💡 장소를 선택하면 해당 장소가 **지도의 정중앙으로 오며 확대**됩니다.")

# API 키 확인
if not KAKAO_REST_API_KEY:
    st.error(f"상위 폴더({env_path})에서 `KAKAO_REST_API_KEY`를 찾을 수 없습니다. `.env` 파일을 확인해주세요.")
    st.stop()

# 기준 위치 설정 (기본값: 서울시청)
DEFAULT_LAT = 37.566535  
DEFAULT_LNG = 126.977969 

with st.sidebar:
    st.header("⚙️ 검색 설정")
    user_lat = st.number_input("기준 위도 (Latitude)", value=DEFAULT_LAT, format="%.6f")
    user_lng = st.number_input("기준 경도 (Longitude)", value=DEFAULT_LNG, format="%.6f")
    st.caption("필요 시 기준 좌표를 변경할 수 있습니다.")

    st.divider()
    st.markdown("### 🏷️ 카테고리 선택")
    
    # 카카오 API 공식 카테고리 코드 매핑
    category_options = {
        "직접 입력하기": "",
        "🍽️ 음식점": "FD6",
        "☕ 카페": "CE7",
        "🏪 편의점": "CS2",
        "🛒 대형마트": "MT1",
        "🏫 학교": "SC4",
        "학원": "AC5",
        "🏨 숙박": "AD5",
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
    
    selected_category_name = st.selectbox("업종 카테고리를 선택하세요:", list(category_options.keys()), key="cat_select")
    selected_category_code = category_options[selected_category_name]

# 검색어 입력 로직
if selected_category_code == "":
    query = st.text_input("검색하고 싶은 키워드를 입력하세요:", key="main_query_input")
else:
    category_clean_name = selected_category_name.split()[-1] if len(selected_category_name.split()) > 1 else selected_category_name
    sub_query = st.text_input(f"[{category_clean_name}] 상세 검색어 (선택 사항 - 비워두면 전체 검색):", key="sub_query_input")
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

    with st.spinner("주변 장소를 검색 중입니다..."):
        response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        documents = data.get("documents", [])

        if documents:
            st.success(f"반경 10km 내에 총 {len(documents)}개의 장소를 찾았습니다 (거리순 정렬)!")

            col1, col2 = st.columns([1, 1.5])

            with col1:
                st.subheader("검색 결과 목록")
                st.caption("버튼을 누르면 선택한 장소가 지도 정중앙으로 확대됩니다.")

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

                    data_text = f" 주소: {address}"
                    st.text(data_text)
                    st.text(f" 거리: 기준 위치로부터 약 {distance_km:.2f} km")
                    if phone != "번호 없음":
                        st.text(f" 연락처: {phone}")
                    
                    st.markdown(f" 🕒 [카카오맵에서 영업시간 및 상세정보 확인하기]({place_url})", unsafe_allow_html=True)
                    st.divider()

            with col2:
                st.subheader("지도 시각화")

                current_idx = st.session_state.selected_idx
                if current_idx >= len(documents):
                    current_idx = 0

                # 선택된 장소의 좌표를 센터로 지정
                selected_place = documents[current_idx]
                center_lat = float(selected_place["y"])
                center_lng = float(selected_place["x"])

                # Folium 지도 생성
                m = folium.Map(location=[center_lat, center_lng], zoom_start=18)

                # 1. 기준 위치 마커 (보라색 집 모양)
                folium.Marker(
                    location=[user_lat, user_lng],
                    popup=folium.Popup("<b>기준 위치</b>", max_width=200),
                    tooltip="🏠 기준 위치",
                    icon=folium.Icon(color="purple", icon="home")
                ).add_to(m)

                # 2. 기준 위치 주변 반경 10km 원 표시
                folium.Circle(
                    location=[user_lat, user_lng],
                    radius=10000,
                    color="#3186cc",
                    fill=True,
                    fill_color="#3186cc",
                    fill_opacity=0.05,
                    tooltip="반경 10km"
                ).add_to(m)

                # 3. 검색된 모든 장소에 마커 표시
                for idx, place in enumerate(documents):
                    lat = float(place["y"])
                    lng = float(place["x"])
                    place_name = place["place_name"]
                    address = place["road_address_name"] or place["address_name"]
                    distance_km = float(place.get("distance", 0)) / 1000
                    place_url = place.get("place_url", "#")

                    if idx == current_idx:
                        icon = folium.Icon(color="blue", icon="star")
                        tooltip_prefix = "⭐ [선택됨] "
                    else:
                        icon = folium.Icon(color="red", icon="info-sign")
                        tooltip_prefix = f"{idx+1}. "

                    popup_html = f"""
                    <div style="width:200px">
                      <b>{place_name}</b><br>
                      {address}<br>
                      거리: {distance_km:.2f}km<br>
                      <a href="{place_url}" target="_blank">카카오맵에서 보기</a>
                    </div>
                    """

                    folium.Marker(
                        location=[lat, lng],
                        popup=folium.Popup(popup_html, max_width=250),
                        tooltip=f"{tooltip_prefix}{place_name} ({distance_km:.2f}km)",
                        icon=icon
                    ).add_to(m)

                # Streamlit에 지도 렌더링
                st_folium(m, width=700, height=550)

        else:
            st.warning("선택하신 조건(반경 10km 내)에 맞는 장소가 없습니다. 카테고리를 변경하거나 검색어를 조정해보세요.")
    else:
        st.error(f"API 호출 중 오류가 발생했습니다. (상태 코드: {response.status_code})")
        st.json(response.json())