import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="나의 첫번째 챗봇", page_icon="🤖")

st.title("예제1) 나의 첫번째 챗봇")
st.caption("질문 하나 입력하면 OpenAI chat Completions API 한번 호출, 답변을 받아오는 가장 단순한 방법")

# --------사이드바 API 모델---
with st.sidebar: 
        st.header("설정")
        api_key = st.text_input("OpenAI API key", type="password", help="sk-로 시작하는 OpenAI키를 입력하세요")
        model = st.selectbox("모델 선택", ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4o"], index=0)
        st.markdown("[API키 발급받기](https://platform.openai.com/api-keys)")


# -----------------메인 화면----
question = st.text_input("질문을 입력하세요", placeholder="예) 오늘 날씨가 어떤가요?")

if st.button("질문하기"):
        if not api_key:
                st.error("OpenAI API Key를 입력하세요.")
        elif not question:
                st.error("질문을 입력하세요.")
        else: 
            try:
                client = OpenAI(api_key=api_key)
                
                # 답변을 생각하는 동안 스피너(로딩 표시) 활용
                with st.spinner("답변을 생각하는 중.."):
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "당신은 친절한 답변가입니다. 모든 답변의 시작은 반드시 '주인님,'으로 시작해야 합니다."},
                            {"role": "user", "content": question}
                        ]
                    )
                
                # 답변 추출
                answer = response.choices[0].message.content
                
                # 화면에 답변 출력
                st.success("답변 완료!")
                st.write(answer)
                
                # 사용한 토큰수 표시
                usage = response.usage
                if usage:
                    st.info(f"📊 사용된 토큰 수 - 입력 토큰: {usage.prompt_tokens}개 / 출력 토큰: {usage.completion_tokens}개 / 총 토큰수: {usage.total_tokens}개")
                    
            except Exception as e:
                # 오류가 발생한 경우 메시지 출력
                st.error(f"오류가 발생했습니다: {e}")
                