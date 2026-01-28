import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="오픈마켓 매출 분석 대시보드", layout="wide")

@st.cache_data
def load_data():
    file_path = '오픈마켓 매출.xlsx - Sheet1.csv'
    try:
        df = pd.read_csv(file_path, encoding='cp949')
    except:
        df = pd.read_csv(file_path, encoding='utf-8')

    # 1. 'Unnamed'가 들어간 열을 모두 삭제
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # 2. 날짜 컬럼 처리
    df['날짜'] = pd.to_datetime(df['날짜'])

    # 3. 데이터 정제: 숫자가 들어있어야 할 열의 NaN을 0으로 채움
    # '날짜' 열을 제외한 나머지 매출 관련 열들 선택
    numeric_cols = df.columns.drop('날짜')
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # 4. 총매출 계산 (순수하게 데이터에 있는 플랫폼들만 합산)
    df['총매출'] = df[numeric_cols].sum(axis=1)
    
    return df

try:
    df = load_data()
    
    # 이제 df.columns에는 실제 플랫폼 이름들만 남게 됩니다.
    platforms = [col for col in df.columns if col not in ['날짜', '총매출']]

    st.title("📈 클린 데이터 매출 분석 대시보드")
    
    # --- 핵심 지표 요약 ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("분석 대상 플랫폼 수", f"{len(platforms)}개")
    with col2:
        st.metric("누적 매출액", f"{df['총매출'].sum():,.0f}원")
    with col3:
        st.metric("최근 데이터 일자", df['날짜'].max().strftime('%Y-%m'))

    st.divider()

    # --- 메인 시각화 ---
    st.subheader("🚀 플랫폼별 매출 기여도 추이")
    # 사용자가 직접 보고 싶은 플랫폼만 선택 가능 (Unnamed 제거됨)
    selected_p = st.multiselect("비교할 플랫폼을 선택하세요", platforms, default=platforms)
    
    if selected_p:
        fig = px.area(df, x='날짜', y=selected_p, 
                      title="플랫폼별 매출 점유 변화",
                      line_group=None)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("분석할 플랫폼을 하나 이상 선택해 주세요.")

    # --- 데이터 표 출력 ---
    with st.expander("원본 데이터 보기 (Unnamed 제거 완료)"):
        st.write(df)

except Exception as e:
    st.error(f"에러 발생: {e}")
