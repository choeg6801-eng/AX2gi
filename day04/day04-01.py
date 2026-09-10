# raw_trade_date.csv 파일 활용

# HS코드가 85로 시작하 (반도체류)

# + 국가명 미국 또는 베트남+ 수출금액 0보다 큰수(실제 수출실적이 있는) 행만

# 다중 조건으로 필터링한 뒤, 수출 금액 상위 10건을 화면에 보여주고 report.csv로 저장

# streamlit 사용 streamlit run day04-01.py6EYS67SUS8US8
#DFDSDDSSD
# sdfsddsdsdsddfs
import streamlit as st
import pandas as pd
import os

st.title("📊 반도체 수출 실적 인터랙티브 분석")

# 데이터 로드
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    paths = [
        os.path.join(current_dir, '../common/raw_trade_data.csv'),
        os.path.join(current_dir, 'common/raw_trade_data.csv'),
        '../common/raw_trade_data.csv',
        './common/raw_trade_data.csv',
        'raw_trade_data.csv'
    ]
    
    df = None
    for path in paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            break
            
    if df is None:
        df = pd.read_csv('../common/raw_trade_data.csv')
        
    return df

df = load_data()

# 컬럼명 앞뒤 공백 제거 및 정제
df.columns = df.columns.str.strip()
df['hs_code'] = df['hs_code'].astype(str).str.strip()
df['국가명'] = df['국가명'].astype(str).str.strip()
df['수출금액'] = pd.to_numeric(df['수출금액'], errors='coerce').fillna(0)

# --- 사이드바(Sidebar) 인터랙티브 컨트롤러 ---
st.sidebar.header("🔍 필터 옵션")

# 1. 국가 선택 (다중 선택 가능)
all_countries = df['국가명'].unique().tolist()
default_countries = [c for c in ['미국', '베트남'] if c in all_countries]
selected_countries = st.sidebar.multiselect(
    "조회할 국가 선택",
    options=all_countries,
    default=default_countries
)

# 2. HS 코드 시작 번호 필터 (기본: 85로 시작)
hs_prefix = st.sidebar.text_input("HS코드 시작 번호", value="85")

# 3. 수출금액 최소값 슬라이더
min_amount = st.sidebar.slider(
    "최소 수출금액 (초과)",
    min_value=0,
    max_value=int(df['수출금액'].max()),
    value=0,
    step=1000000
)

# --- 다중 조건 동적 필터링 ---
cond = (
    df['hs_code'].str.startswith(hs_prefix) & 
    df['국가명'].isin(selected_countries) & 
    (df['수출금액'] > min_amount)
)

filtered_df = df[cond]

# 상위 10건 추출
top10_df = filtered_df.sort_values(by='수출금액', ascending=False).head(10)

# report.csv로 자동 저장
current_dir = os.path.dirname(os.path.abspath(__file__))
report_path = os.path.join(current_dir, 'report.csv')
top10_df.to_csv(report_path, index=False, encoding='utf-8-sig')

# --- 메인 화면 출력 ---
st.subheader(f"📌 필터링된 수출 실적 상위 10건 (총 검색 결과: {len(filtered_df):,}건)")

if len(top10_df) > 0:
    st.dataframe(top10_df, use_container_width=True)
else:
    st.warning("선택한 조건에 일치하는 데이터가 없습니다. 사이드바의 필터 조건을 조정해 보세요.")

# CSV 다운로드 버튼
csv = top10_df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📥 report.csv 다운로드",
    data=csv,
    file_name="report.csv",
    mime="text/csv",
)