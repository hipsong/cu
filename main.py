import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="오픈마켓 연간 매출 추이",
    layout="wide"
)

FILE_PATH = "data/오픈마켓 매출.xlsx"

st.title("📊 네이버 연간 매출 추이 대시보드")

# 1. 파일 체크
if not os.path.exists(FILE_PATH):
    st.error("❌ data/오픈마켓 매출.xlsx 파일을 찾을 수 없습니다.")
    st.stop()

# 2. 엑셀 로드 (Sheet1 고정)
try:
    df = pd.read_excel(FILE_PATH, sheet_name="Sheet1")
except Exception as e:
    st.error("❌ 엑셀 파일을 불러올 수 없습니다.")
    st.exception(e)
    st.stop()

# 3. 컬럼 정리
df = df.rename(columns={df.columns[0]: "월"})

# 월 데이터 정리 (1월~12월만 사용)
df["월_num"] = (
    df["월"]
    .astype(str)
    .str.replace("월", "")
)
df["월_num"] = pd.to_numeric(df["월_num"], errors="coerce")

df = df[df["월_num"].between(1, 12)]

year_cols = [c for c in df.columns if "년" in c]

# 숫자형 변환
for col in year_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.sort_values("월_num")

# ======================
# 📈 월별 매출 추이
# ======================
st.subheader("📈 연도별 월간 매출 추이 (네이버)")

chart_df = df.set_index("월")[year_cols]
st.line_chart(chart_df)

# ======================
# 📊 연간 총매출
# ======================
st.subheader("📊 연도별 연간 총매출")

year_sum = df[year_cols].sum().reset_index()
year_sum.columns = ["연도", "연간 매출"]

st.bar_chart(
    year_sum.set_index("연도")
)

# ======================
# 📄 원본 데이터
# ======================
with st.expander("📄 원본 데이터 보기"):
    st.dataframe(df[["월"] + year_cols], use_container_width=True)

