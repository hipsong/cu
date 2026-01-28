import streamlit as st
import pandas as pd

st.set_page_config(page_title="오픈마켓 매출 대시보드", layout="wide")

FILE_PATH = "data/오픈마켓 매출.xlsx"

st.title("📊 오픈마켓 매출 발표용 대시보드")
st.caption("현재는 네이버 매출만 표시합니다 (추후 확장 가능)")

df = pd.read_excel(FILE_PATH, engine="openpyxl")

# 날짜 컬럼 처리
df["날짜"] = pd.to_datetime(df["날짜"])

st.subheader("📈 네이버 월별 매출 추이")
st.line_chart(
    df.set_index("날짜")["네이버"]
)

st.subheader("📋 원본 데이터")
st.dataframe(df, use_container_width=True)



