import streamlit as st
import pandas as pd

st.set_page_config(page_title="오픈마켓 엑셀 시트 자동 인식", layout="wide")

st.title("📊 오픈마켓 엑셀 시트 자동 인식")

# 1. 파일 업로드
uploaded_file = st.file_uploader(
    "엑셀 파일(xlsx)을 업로드하세요",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("⬆️ 분석할 엑셀 파일을 업로드해 주세요.")
    st.stop()

# 2. 엑셀 파일 열기
try:
    xls = pd.ExcelFile(uploaded_file)
except Exception as e:
    st.error("❌ 엑셀 파일을 읽는 중 오류가 발생했습니다.")
    st.exception(e)
    st.stop()

# 3. 시트 목록
sheet_names = xls.sheet_names
st.success(f"✅ 시트 {len(sheet_names)}개 인식됨")

# 4. 시트 선택
selected_sheet = st.selectbox(
    "확인할 시트를 선택하세요",
    sheet_names
)

# 5. 선택된 시트 로드
try:
    df = pd.read_excel(xls, sheet_name=selected_sheet)
except Exception as e:
    st.error("❌ 시트를 불러오는 중 오류 발생")
    st.exception(e)
    st.stop()

# 6. 데이터 출력
st.subheader(f"📄 [{selected_sheet}] 데이터 미리보기")
st.dataframe(df, use_container_width=True)

# 7. 기본 정보
st.markdown("### ℹ️ 기본 정보")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("행(row)", df.shape[0])

with col2:
    st.metric("열(column)", df.shape[1])

with col3:
    st.metric("결측치 수", int(df.isna().sum().sum()))

