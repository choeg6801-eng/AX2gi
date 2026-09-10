# 인코딩 자동감지 + 한글 폰트 막대그래프 
# 여러 인코딩("utf-8-sig", "cp949","euc-kr") 순서대로 시도 
# 내가 쓸 폰트 같은 경로에 있어야함 
# 객실등급별 생존율 막대 그래프 생성후 그림으로 저장  chart.png
# 실행 streamlit run day03-05.py 

import os
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.title("인코딩 자동감지+ 한글 폰트 막대 그래프(Titanic연습)")
st.caption("여러 인코딩을 순서대로 시도해서 파일을 읽고, 객실등급별 생존율을 그래프로 그립니다.")

csv_PATH = os.path.join(os.path.dirname(__file__), "titanic_cleaned.csv")
Font_path = os.path.join(os.path.dirname(__file__), "Griun_Fromsol-Rg.ttf")


def read_csv_encoding(file_path):
    encodings = ["utf-8-sig", "cp949", "euc-kr"]

    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            st.write(f"'{enc}' 인코딩으로 성공적으로 불러왔습니다.")
            return df
        except (UnicodeDecodeError, UnicodeError):
            continue

    raise ValueError(f"지원하는 인코딩({encodings})으로 파일을 읽을 수 없습니다: {file_path}")


# 1. CSV 파일 읽기
st.subheader("1) 인코딩 자동 감지")
df = read_csv_encoding(csv_PATH)
st.markdown("---")

# 2. 객실등급(Pclass)별 생존율 집계
pclass_survival_rate = df.groupby("Pclass")["Survived"].mean().sort_index()
st.dataframe((pclass_survival_rate * 100).round(1).rename("생존율(%)"))

# 3. 차트 그리기
st.markdown("---")
st.subheader("3) 객실등급별 생존율 막대그래프")

font_prop = None
try:
    font_prop = fm.FontProperties(fname=Font_path)
    fm.fontManager.addfont(Font_path)
    # 한글 전역 폰트 등록 및 마이너스 깨짐 방지
    plt.rc("font", family=font_prop.get_name())
    plt.rc("axes", unicode_minus=False)
    st.write("Griun_Fromsol 폰트를 적용했습니다.")
except FileNotFoundError:
    st.warning("Griun_Fromsol 폰트파일을 찾을 수가 없습니다.")

fig, ax = plt.subplots(figsize=(8, 5))
(pclass_survival_rate * 100).plot(kind="bar", color="skyblue", edgecolor="black", ax=ax)

# 오타 수정: set_xlable -> set_xlabel / set_ylable -> set_ylabel
ax.set_title("객실 등급별 생존율", fontproperties=font_prop)
ax.set_xlabel("객실등급(Pclass)", fontproperties=font_prop)
ax.set_ylabel("생존율(%)", fontproperties=font_prop)
plt.xticks(rotation=0)

# 이미지 파일로 저장
save_path = os.path.join(os.path.dirname(__file__), "chart.png")
fig.savefig(save_path, dpi=300, bbox_inches="tight")

# Streamlit에 표시 
st.pyplot(fig)


