import streamlit as st
import sys
import os

# src 폴더를 파이썬 경로에 추가하여 컴포넌트 모듈 임포트 가능하게 설정
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from components.country_card import render_country_info

# 페이지 기본 설정
st.set_page_config(
    page_title="글로벌 여행 & 국가 정보 가이드",
    page_icon="✈️",
    layout="wide",
)

# 사이드바 네비게이션
st.sidebar.title("🌍 국가별 여행 가이드")
menu = st.sidebar.selectbox(
    "메뉴 선택",
    ["홈 (대한민국)", "중국", "일본", "미국"]
)

# 국가별 데이터 딕셔너리 정의
countries = {
    "홈 (대한민국)": {
        "title": "🇰🇷 대한민국 (Republic of Korea)",
        "subtitle": "활기찬 현대 문화와 전통이 공존하는 매력적인 나라",
        "details": """
        - **수도:** 서울 (Seoul)
        - **언어:** 한국어
        - **통화:** 대한민국 원 (KRW, ₩)
        - **대표 관광지:** 경복궁, 제주도, 부산 해운대, 남이섬
        """,
        "links": {
            "대한민국 구석구석 (한국관광공사)": "https://korean.visitkorea.or.kr",
            "Visit Seoul (서울시 공식 관광 사이트)": "https://www.visitseoul.net"
        },
        "image": "assets/images/korea.jpg"
    },
    "중국": {
        "title": "🇨🇳 중국 (China)",
        "subtitle": "유구한 역사와 광활한 대자연이 펼쳐지는 곳",
        "details": """
        - **수도:** 베이징 (Beijing)
        - **언어:** 중국어 (표준어)
        - **통화:** 위안 (CNY, ¥)
        - **대표 관광지:** 만리장성, 자금성, 상하이 와이탄, 장자제(장가계)
        """,
        "links": {
            "중국 국가문화여유국 공식 포털": "https://www.mct.gov.cn",
            "Travel China Guide": "https://www.travelchinaguide.com"
        },
        "image": "assets/images/china.jpg"
    },
    "일본": {
        "title": "🇯🇵 일본 (Japan)",
        "subtitle": "세련된 도시 감성과 고즈넉한 전통이 어우러진 여행지",
        "details": """
        - **수도:** 도쿄 (Tokyo)
        - **언어:** 일본어
        - **통화:** 엔화 (JPY, ¥)
        - **대표 관광지:** 도쿄 타워, 교토 사찰 군락, 오사카 도톤보리, 후지산
        """,
        "links": {
            "JNTO 일본관광국 공식 사이트 (한국어)": "https://www.japan.travel/ko/kr/"
        },
        "image": "assets/images/japan.jpg"
    },
    "미국": {
        "title": "🇺🇸 미국 (United States)",
        "subtitle": "다양한 문화와 광대한 스케일의 랜드마크가 가득한 나라",
        "details": """
        - **수도:** 워싱턴 D.C. (Washington, D.C.)
        - **언어:** 영어 (사실상 공용어)
        - **통화:** 미국 달러 (USD, $)
        - **대표 관광지:** 뉴욕 타임스퀘어, 그랜드 캐니언, 샌프란시스코 금문교, 로스앤젤레스
        """,
        "links": {
            "GoUSA (미국관광청 공식 사이트)": "https://www.visittheusa.com"
        },
        "image": "assets/images/usa.jpg"
    }
}

# 선택된 국가 정보 렌더링 (컴포넌트 호출)
selected_data = countries[menu]
render_country_info(
    name=menu,
    title=selected_data["title"],
    subtitle=selected_data["subtitle"],
    details=selected_data["details"],
    links=selected_data["links"],
    image_path=selected_data["image"]
)

# 하단 공통 푸터
st.markdown("---")
st.markdown("© 2026 Global Travel Guide App. Built with Streamlit.")