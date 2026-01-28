import streamlit as st
sheets_data = load_all_sheets()
except FileNotFoundError:
st.error("❌ 'data/오픈마켓 매출.xlsx' 파일을 찾을 수 없습니다.")
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
)


# =========================
# KPI 영역
# =========================
st.subheader(f"📌 {selected_market} 연간 매출 요약")
cols = st.columns(len(yearly_sales))


for i, row in yearly_sales.iterrows():
cols[i].metric(
label=row["연도"],
value=f"{row['매출']:,.0f} 원"
)


st.divider()


# =========================
# 월별 매출 추이
# =========================
st.subheader("📈 월별 매출 추이")


fig, ax = plt.subplots()
for year in df_long["연도"].unique():
year_df = df_long[df_long["연도"] == year]
ax.plot(
year_df["월"],
year_df["매출"],
marker="o",
label=year
)


ax.set_xlabel("월")
ax.set_ylabel("매출 (원)")
ax.legend()
ax.grid(True)


st.pyplot(fig)


# =========================
# 연간 총매출 비교
# =========================
st.subheader("📊 연간 총매출 비교")


fig2, ax2 = plt.subplots()
ax2.bar(yearly_sales["연도"], yearly_sales["매출"])
ax2.set_xlabel("연도")
ax2.set_ylabel("매출 (원)")
ax2.grid(axis="y")


st.pyplot(fig2)


# =========================
# 전체 오픈마켓 비교
# =========================
st.divider()
st.subheader("🏬 전체 오픈마켓 연간 매출 비교")


all_data = pd.concat(sheets_data.values())
all_yearly = (
all_data.groupby(["오픈마켓", "연도"])["매출"]
.sum()
.reset_index()
)


pivot_df = all_yearly.pivot(
index="연도",
columns="오픈마켓",
values="매출"
)


st.bar_chart(pivot_df)


# =========================
# 원본 데이터 확인
# =========================
with st.expander("🔍 선택 오픈마켓 원본 데이터"):
st.dataframe(df_long)
