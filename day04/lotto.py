# random 모듈을 이용해서 1~45 중 중복 없는 번호 6개를 뽑고 
# 자료 구조 set(중복 허용 안됨), 버튼을 누르면 5세트 한번에 생성 
# datetime으로 생성 시간도 함께 보여준다
import streamlit as st
import random
from datetime import datetime

st.title("🎱 오늘의 로또 번호 생성기")
st.subheader("🍀행운의 주인공은 바로 당신! 🍀") 
st.caption("버튼을 누르면 1~45 사이의 중복 없는 번호 6개짜리 세트를 5개 생성합니다.")

def lotto_one_set() -> list:
    """1~45에서 중복 없이 번호 6개 뽑아 오름차순 정렬된 리스트로 반환"""
    numbers = set()
    while len(numbers) < 6:
        numbers.add(random.randint(1, 45))
    return sorted(numbers)

def get_ball_html(number: int) -> str:
    """번호 크기에 따라 실제 로또 추첨볼 색상을 입힌 HTML 원형 배지 반환"""
    if 1 <= number <= 10:
        bg_color = "#fbc400"  # 노란색
    elif 11 <= number <= 20:
        bg_color = "#69c8f2"  # 파란색
    elif 21 <= number <= 30:
        bg_color = "#ff7272"  # 빨간색
    elif 31 <= number <= 40:
        bg_color = "#aaaaaa"  # 회색
    else:
        bg_color = "#b0d840"  # 초록색

    return f'<span style="display:inline-block; width:34px; height:34px; line-height:34px; border-radius:50%; background-color:{bg_color}; color:white; text-align:center; font-weight:bold; font-size:14px; margin:2px 4px; box-shadow:1px 1px 3px rgba(0,0,0,0.2);">{number}</span>'

st.markdown("---")

# 버튼을 눌렀을 때만 번호 생성 및 시각 표시
if st.button("🍀 5세트 번호 생성하기", key="lotto_generate_btn"):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"생성 시각: **{now_str}**")
    st.markdown("---")

    for set_index in range(1, 6):
        lotto_num = lotto_one_set()

        # 6개 번호를 각각의 색깔 공 HTML로 변환하여 결합
        balls_html = "".join(get_ball_html(num) for num in lotto_num)

        # 세트 이름과 공들을 한 줄에 출력
        row_content = f"<div style='display:flex; align-items:center; margin-bottom:8px;'><b style='font-size:16px; margin-right:12px;'>{set_index}세트:</b>{balls_html}</div>"
        st.markdown(row_content, unsafe_allow_html=True)
