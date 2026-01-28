import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# =========================
# 기본 설정
# =========================
st.set_page_config(page_title="오픈마켓 연간 매출 대시보드", layout="wide")
st.title("📊 오픈마켓 연간 매출 추이 대시보드")
st.caption("시트별(네이버·쿠팡·11번가 등) 자동 인식")


FILE_PATH = "오픈마켓 매출.xlsx"


# =========================
# 엑셀 시트 자동 인식
# =========================
@st.cache_data
def load_all_sheets():
xls = pd.ExcelFile(FILE_PATH)
sheets = {}
for sheet in xls.sheet_names:
df = pd.read_excel(xls, sheet_name=sheet)
df = df.rename(columns={df.columns[0]: "월"})
df_long = df.melt(id_vars="월", var_name="연도", value_name="매출")
df_long["매출"] = pd.to_numeric(df_long["매출"], errors="coerce")
df_long["오픈마켓"] = sheet
sheets[sheet] = df_long
return sheets


sheets_data = load_all_sheets()


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
)


# =========================
# KPI
# =========================
st.subheader(f"📌 {selected_market} 연간 매출 요약")
cols = st.columns(len(yearly_sales))


for i, row in yearly_sales.iterrows():
cols[i].metric(row["연도"], f"{row['매출']:,.0f} 원")


st.divider()


# =========================
# 월별 추이
# =========================
st.subheader("📈 월별 매출 추이")
fig, ax = plt.subplots()


for year in df_long["연도"].unique():
ydf = df_long[df_long["연도"] == year]
ax.plot(ydf["월"], ydf["매출"], marker="o", label=year)


ax.set_xlabel("월")
ax.set_ylabel("매출 (원)")
ax.legend()
ax.grid(True)
st.pyplot(fig)


# =========================
# 연간 비교
# =========================
