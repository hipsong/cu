import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정 (최상단 고정)
st.set_page_config(page_title="cu메디컬 오픈마켓 매출 분석", layout="wide")

@st.cache_data
def load_and_clean_data():
    file_path = '오픈마켓 매출.csv'
    try:
        df = pd.read_csv(file_path, encoding='cp949')
    except:
        df = pd.read_csv(file_path, encoding='utf-8-sig')

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['날짜'] = pd.to_datetime(df['날짜'])
    
    numeric_cols = df.columns.drop('날짜')
    for col in numeric_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # 만원 단위 변환
    for col in numeric_cols:
        df[f"{col}_만원"] = df[col] / 10_000
        
    df['월간총매출_만원'] = df[numeric_cols].sum(axis=1) / 10_000
    df['연도'] = df['날짜'].dt.year
    
    return df, numeric_cols.tolist()

try:
    df, platforms = load_and_clean_data()
    platforms_man = [f"{p}_만원" for p in platforms]
    display_map = {f"{p}_만원": p for p in platforms}

    # 헤더 섹션
    st.title("🏥 CU메디컬 매출 성과 분석 대시보드")
    
    # KPI 지표 (상단 카드)
    total_rev_billion = df['월간총매출_만원'].sum() / 10000
    max_month_val = df['월간총매출_만원'].max()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("전체 누적 매출", f"{total_rev_billion:.2f} 억 원")
    c2.metric("역대 최고 월 매출", f"{max_month_val:,.0f} 만원")
    c3.metric("데이터 집계 기간", f"{df['연도'].min()}년 ~ {df['연도'].max()}년")

    st.divider()

    # --- 메인 분석 영역 (탭 구조) ---
    tab1, tab2 = st.tabs(["📈 월간 총매출 추이", "📊 연간 실적 분석"])

    with tab1:
        st.subheader("🗓️ 회사 월별 통합 매출 흐름")
        
        # 1. 회사 전체 월별 매출 (Area Chart)
        fig_monthly_total = px.area(df, x='날짜', y='월간총매출_만원',
                                    title="전체 플랫폼 합산 월 매출 추이",
                                    color_discrete_sequence=['#FF4B4B'])
        fig_monthly_total.update_layout(yaxis_title="매출액 (만원)", yaxis=dict(tickformat=",.0f"), hovermode="x unified")
        fig_monthly_total.update_traces(fillcolor='rgba(255, 75, 75, 0.2)')
        st.plotly_chart(fig_monthly_total, use_container_width=True)

        # 2. 플랫폼별 기여도 추이 (Stacked Area)
        st.write("#### 🔍 플랫폼별 매출 기여 비중")
        selected_p = st.multiselect("비교 플랫폼 선택", platforms, default=platforms)
        selected_p_man = [f"{p}_만원" for p in selected_p]
        
        if selected_p_man:
            fig_stack = px.area(df, x='날짜', y=selected_p_man, labels=display_map,
                                color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_stack.update_layout(yaxis_title="매출액 (만원)", hovermode="x unified")
            st.plotly_chart(fig_stack, use_container_width=True)

    with tab2:
        st.subheader("📅 연도별 전사 성과 분석")
        
        # 연도별 데이터 그룹화
        yearly_df = df.groupby('연도')['월간총매출_만원'].sum().reset_index()
        yearly_df.columns = ['연도', '연간총매출_만원']
        # 성장률 계산
        yearly_df['성장률'] = yearly_df['연간총매출_만원'].pct_change() * 100

        col_left, col_right = st.columns([7, 3])
        
        with col_left:
            fig_year = px.bar(yearly_df, x='연도', y='연간총매출_만원',
                              text_auto=',.0f', title="연도별 총 매출 규모 (만원)")
            fig_year.update_traces(marker_color='#007BFF', textposition='outside')
            fig_year.update_layout(xaxis=dict(type='category'), yaxis_title="매출액 (만원)")
            st.plotly_chart(fig_year, use_container_width=True)
            
        with col_right:
            st.write("#### 연도별 요약 리포트")
            report_df = yearly_df.copy()
            report_df['매출액'] = report_df['연간총매출_만원'].map('{:,.0f} 만'.format)
            report_df['성장률(YoY)'] = report_df['성장률'].map(lambda x: f"{x:+.1f}%" if pd.notnull(x) else "-")
            st.table(report_df[['연도', '매출액', '성장률(YoY)']].set_index('연도'))

    # 데이터 테이블
    with st.expander("📝 원본 데이터 상세 확인 (단위: 만원)"):
        st.dataframe(df[['날짜'] + platforms_man + ['월간총매출_만원']].sort_values('날짜', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
    st.info("파일명이 '오픈마켓 매출.csv'인지 확인해 주세요.")
