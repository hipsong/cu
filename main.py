import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="오픈마켓 매출 분석 대시보드", layout="wide")

# 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_csv('오픈마켓 매출.csv')
    df['날짜'] = pd.to_datetime(df['날짜'])
    # 총 매출 계산
    df['총매출'] = df.iloc[:, 1:].sum(axis=1)
    return df

try:
    df = load_data()

    st.title("📈 오픈마켓 매출 분석 대시보드")
    st.markdown("전체 플랫폼의 매출 추이와 마켓별 성과를 분석합니다.")

    # --- 상단 지표 (KPI) ---
    col1, col2, col3 = st.columns(3)
    total_sales = df['총매출'].sum()
    avg_sales = df['총매출'].mean()
    max_month = df.loc[df['총매출'].idxmax(), '날짜'].strftime('%Y-%m')

    col1.metric("누적 총 매출", f"{total_sales:,.0f}원")
    col2.metric("월 평균 매출", f"{avg_sales:,.0f}원")
    col3.metric("최고 매출 월", max_month)

    st.divider()

    # --- 메인 그래프: 매출 추이 ---
    st.subheader("🗓️ 월별 매출 통합 추이")
    tab1, tab2 = st.tabs(["라인 차트", "누적 영역 차트"])
    
    with tab1:
        fig_line = px.line(df, x='날짜', y=['네이버', '공식몰', '지마켓', '옥션', '쿠팡', '11번가'], 
                          title="플랫폼별 매출 흐름")
        st.plotly_chart(fig_line, use_container_width=True)
    
    with tab2:
        fig_area = px.area(df, x='날짜', y=['네이버', '공식몰', '지마켓', '옥션', '쿠팡', '11번가'], 
                          title="플랫폼별 매출 비중 추이")
        st.plotly_chart(fig_area, use_container_width=True)

    # --- 상세 분석 섹션 ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 플랫폼별 매출 점유율")
        platform_sums = df.iloc[:, 1:-1].sum().sort_values(ascending=False)
        fig_pie = px.pie(values=platform_sums.values, names=platform_sums.index, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.subheader("🔍 데이터 상세보기")
        st.dataframe(df.sort_values('날짜', ascending=False), height=400)

    # --- 분석 인사이트 ---
    st.sidebar.header("분석 옵션")
    selected_platform = st.sidebar.selectbox("상세 분석할 플랫폼 선택", df.columns[1:-1])
    
    st.sidebar.write(f"**{selected_platform}** 분석 결과:")
    platform_growth = ((df[selected_platform].iloc[-1] / df[selected_platform].iloc[0]) - 1) * 100
    st.sidebar.write(f"- 기간 내 성장률: {platform_growth:.2f}%")

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.info("CSV 파일명이 '오픈마켓 매출.xlsx - Sheet1.csv'인지 확인해 주세요.")

