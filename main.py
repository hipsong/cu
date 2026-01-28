import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="네이버 매출", layout="wide")

FILE_PATH = "data/오픈마켓 매출.csv"

st.title("📊 네이버 월별 매출")

# 1. 파일 존재 확인
if not os.path.exists(FILE_PATH):
    st.error("❌ CSV 파일을 찾을 수 없습니다.")
    st.stop()

# 2. CSV 읽기 (인코딩 자동 시도)
try:
    try:
        df = pd.read_csv(FILE_PATH, encoding="utf-8")
    except:
        df = pd.read_csv(FILE_PATH, encoding="cp949")
except Exception as e:
    st.error("❌ CSV 파일을 읽는 중 오류 발생")
    st.exception(e)
    st.stop()

# 3. 원본 데이터 확인
st.subheader("원본 데이터 (네이버 매출)")
st.dataframe(df, use_container_width=True)

# 4. 컬럼 구조 정리
# 첫 컬럼 = 월, 나머지 = 연도
df = df.rename(columns={df.columns[0]: "월"})

# 5. 연도 선택
year_cols = [col for col in df.columns if col != "월"]
selected_year = st.selectbox("연도 선택", year_cols)

# 6. 데이터 타입 정리
df["월"] = pd.to_numeric(df["월"], errors="coerce")
df[selected_year] = (
    df[selected_year]
    .astype(str)
    .str.replace(",", "")
    .str.replace("₩", "")
)
df[selected_year] = pd.to_numeric(df[selected_year], errors="coerce")

df = df.dropna()

# 7. 차트
chart_df = df.sort_values("월").set_index("월")[[selected_year]]

st.subheader(f"📈 네이버 매출 추이 ({selected_year})")
st.line_chart(chart_df)
