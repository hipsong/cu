import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="오픈마켓 매출 분석", layout="wide")

@st.cache_data
def load_and_clean_data():
    file_path = '오픈마켓 매출.csv'
    
    # 1. 인코딩 문제 해결하며 불러오기
    try:
        df = pd.read_csv(file_path, encoding='cp949')
    except:
        df = pd.read_csv(file_path, encoding='utf-8-sig')

    # 2. 'Unnamed'로 시작하는 모든 열 삭제
    # 분석에 불필요한 빈 열들을 제거합니다.
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # 3. 데이터 정제 (날짜 형식 변환 및 결측치 0 채우기)
    df['날짜'] = pd.to_datetime(df['날짜'])
    numeric_cols = df.columns.drop('날짜')
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # 4. 총매출 계산
    df['총매출'] = df[numeric_cols].sum(axis=1)
    
    return df, numeric_cols.tolist()

try:
    # 데이터 불러오기
    df, platforms = load_and_clean_data()

    st.title("📊 오픈마켓 매출 성과 대시보드 (main.py)")
    
    # 상단 요약 지표
    col1, col2, col3 = st.columns(3)
    col1.metric("총 누적 매출", f"{df['총매출'].sum():,.0f}원")
    col2.metric("분석 플랫폼", f"{len(platforms)}개")
    col3.metric("최근 데이터", df['날짜'].max().strftime('%Y-%m'))

    st.divider()

    # 메인 그래프: 매출 추이
    st.subheader("📈 월별 매출 추이 분석")
    selected_p = st.multiselect("확인할 플랫폼을 선택하세요", platforms, default=platforms)
    
    if selected_p:
        # Plotly를 이용한 선 그래프
        fig = px.line(df, x='날짜', y=selected_p, markers=True, 
                      title="플랫폼별 매출 흐름")
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
        
        # 플랫폼별 비중 차트
        st.subheader("🥧 플랫폼별 점유율 (누적)")
        pie_data = df[selected_p].sum()
        fig_pie = px.pie(values=pie_data.values, names=pie_data.index, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("분석할 플랫폼을 선택해 주세요.")

    # 데이터 확인용 표
    with st.expander("정제된 데이터 상세보기"):
        st.dataframe(df)

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
