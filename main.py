import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="네이버 매출", layout="wide")

FILE_PATH = "data/오픈마켓 매출.xlsx"

st.title("📊 네이버 월별 매출")

# 1. 파일 존재 여부 확인
if not os.path.exists(FILE_PATH):
    st.error("❌ 엑셀 파일을 찾을 수 없습니다.")
    st.stop()

# 2. Sheet1만 명시적으로 읽기
try:
    df = pd.read_excel(FILE_PATH, sheet_name=0)
except Exception as e:
    st.error("❌ 엑셀 파일을 읽는 중 오류 발생")
    st.exception(e)
    st.stop()

# 3. 데이터 미리보기
st.subheader("원본 데이터")
st.dataframe(df, use_container_width=True)

# 4. 컬럼 정리
# 첫 컬럼: 월, 나머지: 연도
df = df.rename(columns={df.columns[0]: "월"})

# 5. 연도 선택
years = [col for col in df.columns if col != "월"]
selected_year = st.selectbox("연도 선택", years)

# 6. 차트용 데이터
chart_df = df[["월", selected_year]].set_index("월")

st.subheader(f"📈 네이버 매출 추이 ({selected_year})")
st.line_chart(chart_df)


