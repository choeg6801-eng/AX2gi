import streamlit as st

st.title("🧮 심플 사칙연산 계산기")
st.subheader("Streamlit으로 만든 간단한 계산기입니다.")
st.caption("두 개의 숫자와 연산자를 선택하면 자동으로 계산 결과가 나타납니다.")

st.markdown("---")

# 입력 영역을 2개의 열로 나누어 배치
col1, col2 = st.columns(2)

with col1:
    num1 = st.number_input("첫 번째 숫자 입력", value=0.0, step=1.0, format="%f")

with col2:
    num2 = st.number_input("두 번째 숫자 입력", value=0.0, step=1.0, format="%f")

# 연산자 선택
operator = st.selectbox(
    "연산자 선택",
    ("+ (더하기)", "- (빼기)", "× (곱하기)", "÷ (나누기)"),
    index=0
)

st.markdown("---")

# 사칙연산 수행
result = None
error_msg = None

if operator == "+ (더하기)":
    result = num1 + num2
    op_symbol = "+"
elif operator == "- (빼기)":
    result = num1 - num2
    op_symbol = "-"
elif operator == "× (곱하기)":
    result = num1 * num2
    op_symbol = "×"
elif operator == "÷ (나누기)":
    if num2 == 0:
        error_msg = "❌ 0으로 나눌 수 없습니다!"
    else:
        result = num1 / num2
    op_symbol = "÷"

# 결과 출력
st.subheader("📊 계산 결과")
if error_msg:
    st.error(error_msg)
else:
    # 소수점 이하 자리수가 .0으로 끝나는 경우 깔끔하게 표현하기 위해 정수 처리
    display_num1 = int(num1) if num1.is_integer() else num1
    display_num2 = int(num2) if num2.is_integer() else num2
    display_result = int(result) if isinstance(result, float) and result.is_integer() else result

    st.success(f"**{display_num1} {op_symbol} {display_num2} = {display_result}**")
