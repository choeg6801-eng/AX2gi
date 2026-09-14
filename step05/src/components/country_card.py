import streamlit as st

def render_country_info(name, title, subtitle, details, links, image_path):
    st.title(title)
    st.subheader(subtitle)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(details)
        st.markdown("### 🔗 공식 여행 사이트")
        for link_name, link_url in links.items():
            st.markdown(f"- [{link_name}]({link_url})")
            
    with col2:
        try:
            st.image(image_path, caption=name, use_container_width=True)
        except Exception:
            st.info(f"💡 {image_path} 경로에 이미지를 추가해 보세요!")