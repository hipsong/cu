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

# 2. CSV 읽기 (구분자 + 인코딩 자동 추론)
try:
    df = pd.read_csv(
        FILE_PATH,
        engine="python",
        sep=None,          # ← 구분자 자동 인식
        encoding="utf-8",
        skip_blank_lines=True
    )
except:
    try:
        df = pd.read_csv(
            FILE_PATH,
            engine="python",
            sep=None,
            encoding="cp949",
            skip_blank_lines=True
        )
    except Exception as e:
        st.error("❌ CSV 파일을 읽을 수 없습니다.")
        st.exception(e)
        st.stop()

# 3. 데이터 존재 여부 확인
if df.empty:
    st.error("❌ CSV 파일에 데이터가 없습니다.")
    st.stop()

# 4. 원본 데이터 표시
st.subheader("원본 데이터 (네이버 매출)")
st.dataframe(df, use_container_width=True)

# 5. 컬럼 구조 정리
df = df.rename(columns={df.columns[0]: "월"})

# 6. 연도 컬럼 추출
year_cols = [col for col in df.columns if col != "월"]
if not year_cols:
    st.error("❌ 연도 컬럼을 찾을 수 없습니다.")
    st.stop()

selected_year = st.selectbox("연도 선택", year_cols)

# 7. 데이터 타입 정리
df["월"] = pd.to_numeric(df["월"], errors="coerce")

df[selected_year] = (
    df[selected_year]
    .astype(str)
    .str.replace(",", "")
    .str.replace("₩", "")
    .str.strip()
)
df[selected_year] = pd.to_numeric(df[selected_year], errors="coerce")

df = df.dropna()

# 8. 차트
chart_df = df.sort_values("월").set_index("월")[[selected_year]]

st.subheader(f"📈 네이버 매출 추이 ({selected_year})")
st.line_chart(chart_df)
