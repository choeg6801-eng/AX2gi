import os
import streamlit as st
from dotenv import load_dotenv

# 현재 폴더 및 상위 폴더의 .env 파일 로드 시도
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")

st.set_page_config(
    page_title="카카오 맵 API 연동 스트림릿",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ 카카오 맵 API 연동 예제")
st.write("스트림릿과 카카오 JavaScript SDK를 활용해 서울 주요 명소 마커를 표시합니다.")

# .env에서 키를 못 읽어왔을 경우 화면에서 직접 입력받는 입력창 제공
if not KAKAO_API_KEY or KAKAO_API_KEY == "여러분의_카카오_자바스크립트_API_키_입력":
    st.warning("⚠️ `.env` 파일에서 API 키를 찾지 못했습니다. 아래 칸에 카카오 JavaScript API 키를 직접 입력해 주세요.")
    KAKAO_API_KEY = st.text_input("카카오 JavaScript API 키", type="password")

# 키가 입력된 경우에만 지도 렌더링
if not KAKAO_API_KEY:
    st.error("⚠️ 지도를 띄우려면 카카오 API 키를 입력해주세요!")
else:
    kakao_map_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>카카오 지도</title>
        <style>
            #map {{
                width: 100%;
                height: 500px;
                border-radius: 10px;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_API_KEY}"></script>
        <script>
            var container = document.getElementById('map');
            var options = {{
                center: new kakao.maps.LatLng(37.5666, 126.9784),
                level: 7
            }};
            var map = new kakao.maps.Map(container, options);

            var positions = [
                {{ title: '경복궁', lat: 37.5796, lng: 126.9770 }},
                {{ title: '남산타워', lat: 37.5512, lng: 126.9882 }},
                {{ title: '롯데월드', lat: 37.5111, lng: 127.0982 }},
                {{ title: '한강', lat: 37.5219, lng: 126.9244 }}
            ];

            for (var i = 0; i < positions.length; i++) {{
                var marker = new kakao.maps.Marker({{
                    map: map,
                    position: new kakao.maps.LatLng(positions[i].lat, positions[i].lng),
                    title: positions[i].title
                }});

                var infowindow = new kakao.maps.InfoWindow({{
                    content: '<div style="padding:5px;font-size:12px;">' + positions[i].title + '</div>'
                }});
                infowindow.open(map, marker);
            }}
        </script>
    </body>
    </html>
    """
    st.components.v1.html(kakao_map_html, height=520)

st.markdown("---")
st.info("💡 카카오 개발자 콘솔(Developers)에서 앱 설정 > 플랫폼의 **Web 도메인**에 `http://localhost:8501`이 등록되어 있어야 지도가 정상적으로 출력됩니다.")