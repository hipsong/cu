import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="네이버 매출", layout="wide")

FILE_PATH = "data/오픈마켓 매출.csv"

st.title("📊 네이버 월별 매출")

if not os.path.exists(FILE_PATH):
    st.error("❌ CSV 파일을 찾을 수 없습니다.")
    st.stop()

# 1. CSV 로드 (구분자 총공세)
df = None
errors = []

for encoding in ["utf-8", "cp949"]:
    for sep in [",", ";", "\t", "|"]:
        try:
            temp = pd.read_csv(
                FILE_PATH,
                encoding=encoding,
                sep=sep
            )
            if temp.shape[1] > 1:  # 컬럼이 2개 이상이면 성공
                df = temp
                break
        except Exception as e:
            errors.append(f"encoding={encoding}, sep='{sep}' → {e}")
    if df is not None:
        break

if df is None:
    st.error("❌ CSV 파일을 해석할 수 없습니다.")
    st.write("시도한 경우:")
    for e in errors:
        st.write(e)
    st.stop()

# 2. 원본 데이터 확인
st.subheader("원본 데이터 (네이버 매출)")
st.dataframe(df, use_container_width=True)

# 3. 컬럼 구조 정리
df = df.rename(columns={df.columns[0]: "월"})

# 4. 연도 컬럼 추출
year_cols = [c for c in df.columns if c != "월"]
if not year_cols:
    st.error("❌ 연도 컬럼을 찾을 수 없습니다.")
    st.stop()

selected_year = st.selectbox("연도 선택", year_cols)

# 5. 데이터 타입 정리
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

# 6. 차트
chart_df = df.sort_values("월").set_index("월")[[selected_year]]

st.subheader(f"📈 네이버 매출 추이 ({selected_year})")
st.line_chart(chart_df)
