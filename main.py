import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =============================
# 기본 설정
# =============================
st.set_page_config(page_title="오픈마켓 매출 대시보드", layout="wide")

FILE_PATH = "오픈마켓 매출.xlsx"

st.title("📊 오픈마켓 매출 발표용 대시보드")
st.caption("현재는 네이버 매출만 표시합니다 (추후 확장 가능)")

# =============================
# 데이터 로드
# =============================
@st.cache_data
def load_data():
    try:
        df = pd.read_excel(FILE_PATH, engine="openpyxl")
        return df
    except Exception as e:
        st.error(f"파일을 불러오지 못했습니다: {e}")
        return None

df = load_data()

if df is None:
    st.stop()

# =============================
# 컬럼 자동 탐색
# =============================
# 예상 컬럼명 대응 (유연하게 처리)
col_date = next((c for c in df.columns if "일" in c or "date" in c.lower()), None)
col_market = next((c for c in df.columns if "마켓" in c or "몰" in c), None)
col_sales = next((c for c in df.columns if "매출" in c or "금액" in c), None)

if not all([col_date, col_market, col_sales]):
    st.error("필수 컬럼(날짜, 마켓, 매출)을 자동으로 찾지 못했습니다")
    st.write(df.head())
    st.stop()

# =============================
# 네이버 매출 필터
# =============================
naver_df = df[df[col_market].astype(str).str.contains("네이버")].copy()

naver_df[col_date] = pd.to_datetime(naver_df[col_date])
naver_df = naver_df.sort_values(col_date)

# =============================
# KPI 영역
# =============================
total_sales = naver_df[col_sales].sum()
max_sales = naver_df[col_sales].max()

c1, c2 = st.columns(2)
c1.metric("네이버 총 매출", f"{total_sales:,.0f} 원")
c2.metric("일 최대 매출", f"{max_sales:,.0f} 원")

# =============================
# 시계열 차트
# =============================
st.subheader("📈 네이버 일별 매출 추이")

fig = plt.figure()
plt.plot(naver_df[col_date], naver_df[col_sales])
plt.xticks(rotation=45)
plt.ylabel("매출")
plt.xlabel("날짜")
plt.tight_layout()

st.pyplot(fig)

# =============================
# 원본 데이터
# =============================
with st.expander("원본 데이터 보기"):
    st.dataframe(naver_df)


