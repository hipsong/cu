import streamlit as st
import pandas as pd
import os

# =========================
# 기본 설정
# =========================
st.set_page_config(
    page_title="오픈마켓 연간 매출 대시보드",
    layout="wide"
)

st.title("📊 오픈마켓 연간 매출 추이 대시보드")
st.caption("엑셀 시트별(네이버·쿠팡·11번가 등) 자동 인식")

# =========================
# 파일 경로 설정
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "data", "오픈마켓 매출.xlsx")

# =========================
# 엑셀 시트 자동 로드
# =========================
@st.cache_data
@st.cache_data
def load_all_sheets(file_path):
    xls = pd.ExcelFile(file_path, engine="openpyxl")
    sheets = {}

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, engine="openpyxl")
        df = df.rename(columns={df.columns[0]: "월"})

        df_long = df.melt(
            id_vars="월",
            var_name="연도",
            value_name="매출"
        )

        df_long["매출"] = pd.to_numeric(df_long["매출"], errors="coerce")
        df_long["오픈마켓"] = sheet

        sheets[sheet] = df_long

    return sheets

# =========================
# 데이터 로딩
# =========================
try:
    sheets_data = load_all_sheets(FILE_PATH)
except FileNotFoundError:
    st.error("❌ data/오픈마켓 매출.xlsx 파일을 찾을 수 없습니다.")
    st.stop()

# =========================
# 오픈마켓 선택
# =========================
st.sidebar.header("🛒 오픈마켓 선택")
market_list = list(sheets_data.keys())
selected_market = st.sidebar.selectbox("분석할 오픈마켓", market_list)

df_long = sheets_data[selected_market]

# =========================
# 연간 매출 집계
# =========================
yearly_sales = (
    df_long.groupby("연도")["매출"]
    .sum()
    .reset_index()
    .set_index("연도")
)

# =========================
# KPI
# =========================
st.subheader(f"📌 {selected_market} 연간 매출 요약")
cols = st.columns(len(yearly_sales))

for i, (year, value) in enumerate(yearly_sales["매출"].items()):
    cols[i].metric(year, f"{value:,.0f} 원")

st.divider()

# =========================
# 월별 매출 추이 (라인 차트)
# =========================
st.subheader("📈 월별 매출 추이")

monthly_pivot = df_long.pivot(
    index="월",
    columns="연도",
    values="매출"
)

st.line_chart(monthly_pivot)

# =========================
# 연간 총매출 비교
# =========================
st.subheader("📊 연간 총매출 비교")

st.bar_chart(yearly_sales)

# =========================
# 전체 오픈마켓 비교
# =========================
st.divider()
st.subheader("🏬 전체 오픈마켓 연간 매출 비교")

all_data = pd.concat(sheets_data.values())
all_yearly = (
    all_data.groupby(["연도", "오픈마켓"])["매출"]
    .sum()
    .reset_index()
)

pivot_all = all_yearly.pivot(
    index="연도",
    columns="오픈마켓",
    values="매출"
)

st.bar_chart(pivot_all)

# =========================
# 원본 데이터
# =========================
with st.expander("🔍 선택 오픈마켓 원본 데이터"):
    st.dataframe(df_long)
