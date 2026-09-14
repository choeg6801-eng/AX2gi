import streamlit as st

st.set_page_config(page_title="세계 여행 포털", page_icon="🌍")

# 사이드바 메뉴 생성
menu = st.sidebar.radio("메뉴", ["홈", "미국", "중국", "일본"])

if menu == "홈":
    st.subheader("대한민국 (South Korea)")
    st.write("대한민국은 동아시아에 위치한 나라로, 한반도의 남쪽에 자리잡고 있습니다.")
    st.write("전통과 현대가 공존하는 매력적인 문화 중심지입니다.")

elif menu == "미국":
    st.subheader("미국 (United States)")
    st.write("미국은 북아메리카에 위치한 연방제로, 다양한 인종과 문화가 어우러진 거대한 국가입니다.")
    st.write("자연 경관부터 뉴욕, 로스앤젤레스 같은 대도시까지 다양한 볼거리가 있습니다.")
    
    # 미국 공식 관광 사이트 링크 버튼 수정
    st.link_button("미국공식사이트방문", "https://www.visittheusa.com")

elif menu == "중국":
    st.subheader("중국 (China)")
    st.write("중국은 유구한 역사와 광대한 영토를 가진 동아시아의 국가입니다.")
    st.write("만리장성, 자금성 등 세계적인 문화유산과 다채로운 미식 문화를 자랑합니다.")
    
    # 중국 공식 관광 사이트 링크 버튼 추가
    st.link_button("중국공식사이트방문", "https://www.travelchinaguide.com/")

elif menu == "일본":
    st.subheader("일본 (Japan)")
    st.write("일본은 동아시아에 위치한 섬나라로, 사계절의 뚜렷한 자연美가 돋보입니다.")
    st.write("오래된 전통 사찰과 최첨단 도시 문화를 동시에 경험할 수 있는 인기 여행지입니다.")
    
    # 일본 공식 관광 사이트 링크 버튼 추가
    st.link_button("일본공식사이트방문", "https://www.japan.travel/ko/")