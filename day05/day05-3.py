import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="나의 첫번째 챗봇", page_icon="🤖")

st.title("예제) 대화 기록을 기억하는 멀티턴 챗봇")
st.caption("스트리밍 응답, 시스템 메시지 설정, 대화 초기화 기능이 포함된 Streamlit 챗봇입니다.")

# -------- 사이드바 설정 ---
with st.sidebar: 
    st.header("설정")
    api_key = st.text_input("OpenAI API key", type="password", help="sk-로 시작하는 OpenAI키를 입력하세요")
    model = st.selectbox("모델 선택", ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4o"], index=0)
    
    st.divider()
    
    # 시스템 메시지 사용자 설정
    system_message = st.text_area(
        "시스템 메시지", 
        value="당신은 친절한 답변가입니다.",
        help="챗봇의 페르소나나 역할을 지정할 수 있습니다."
    )
    
    st.divider()
    
    # 대화 기록 초기화 버튼
    if st.button("대화 기록 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("[API키 발급받기](https://platform.openai.com/api-keys)")


# -------- 세션 상태 초기화 (대화 기록 저장용) ---
if "messages" not in st.session_state:
    st.session_state.messages = []


# -------- 기존 대화 기록 화면에 출력 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -------- 사용자 입력 (채팅 입력창) ---
if prompt := st.chat_input("질문을 입력하세요..."):
    if not api_key:
        st.error("OpenAI API Key를 입력하세요.")
    else: 
        # 사용자 메시지를 세션에 저장하고 화면에 즉시 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            client = OpenAI(api_key=api_key)
            
            # API에 전달할 메시지 구성 (시스템 메시지 + 전체 대화 히스토리)
            messages_payload = []
            if system_message:
                messages_payload.append({"role": "system", "content": system_message})
            messages_payload.extend(st.session_state.messages)
            
            # OpenAI API 호출 (stream=True 적용)
            with st.chat_message("assistant"):
                stream = client.chat.completions.create(
                    model=model,
                    messages=messages_payload,
                    stream=True
                )
                
                # st.write_stream을 활용해 타이핑 효과처럼 실시간 출력 및 전체 응답 텍스트 반환 받기
                answer = st.write_stream(stream)
            
            # 어시스턴트의 최종 답변을 세션 대화 기록에 저장
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")