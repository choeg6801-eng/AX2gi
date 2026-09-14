import streamlit as st

st.set_page_config(page_title="세계 여행 포털", page_icon="🌍")

# title에 국가 이모지 적용
home_page = st.Page("view/home.py", title="🇰🇷 대한민국", icon="🏠", default=True)
usa = st.Page("view/US.py", title="🇺🇸 미국", icon="🗽")
china = st.Page("view/china.py", title="🇨🇳 중국", icon="🐼")
japan = st.Page("view/japan.py", title="🇯🇵 일본", icon="⛩️")

# 네비게이션 설정
pg = st.navigation([home_page, usa, china, japan])

# 페이지 실행
pg.run()
