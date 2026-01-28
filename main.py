import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="전사 매출 분석 시스템", layout="wide")

@st.cache_data
def load_and_clean_data():
    file_path = '오픈마켓 매출.csv'
    try:
        df = pd.read_csv(file_path, encoding='cp949')
    except:
        df = pd.read_csv(file_path, encoding='utf-8-sig')

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['날짜'] = pd.to_datetime(df['날짜'])
    
    # 숫자형 데이터 정제 (콤마 제거 및 수치화)
    numeric_cols = df.columns.drop('날짜')
    for col in numeric_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # 단위 변환: 만원
    for col in numeric_cols:
        df[f"{col}_만원"] = df[col] / 10_000
        
    df['월간총매출_만원'] = df[numeric_cols].sum(axis=1) / 10_000
    df['연도'] = df['날짜'].dt.year
    
    return df, numeric_cols.tolist()

try:
    df, platforms = load_and_clean_data()
    platforms_man = [f"{p}_만원" for p in platforms]
    display_map = {f"{p}_만원": p for p in platforms}

    st.title("🏢 전사 매출 분석 대시보드")
    
    # 상단 요약 KPI
    c1, c2, c3 = st.columns(3)
    total_revenue_billion = df['월간총매출_만원'].sum() / 10000
    c1.metric("총 누적 매출액", f"{total_revenue_billion:.2f} 억 원")
    c2.metric("최고 월 매출액", f"{df['월간총매출_만원'].max():,.0f} 만원")
    c3.metric("데이터 집계 기간", f"{df['연도'].min()}년 ~ {df['연도'].max()}년")

    st.divider()

    # --- 매출 추이 분석 섹션 ---
    tab1, tab2 = st.tabs(["📅 월간 매출 추이", "📅 연간 매출 분석"])

    with tab1:
        st.subheader("회사의 월별 총 매출 흐름")
        # 전체 통합 차트 (영역 강조)
        fig_month = px.area(df, x='날짜', y='월간총매출_만원', 
                            title="전체 플랫폼 통합 월 매출 추이 (만원)")
        fig_month.update_traces(line_color='#FF4B4B', fillcolor='rgba(255, 75, 75, 0.2)')
        fig_month.update_layout(yaxis_title="매출액 (만원)", yaxis=dict(tickformat=",.0f"), hovermode="x unified")
        st.plotly_chart(fig_month, use_container_width=True)
        
        st.write("#### 📊 플랫폼별 상세 기여도")
        fig_stack = px.area(df, x='날짜', y=platforms_man, labels=display_map,
                            color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_stack.update_layout(yaxis_title="매출액 (만원)", hovermode="x unified")
        st.plotly_chart(fig_stack, use_container_width=True)

    with tab2:
        st.subheader("연도별 총 성과 분석")
        # 연도별 데이터 가공
        yearly_df = df.groupby('연도')['월간총매출_만원'].sum().reset_index()
        yearly_df.columns = ['연도', '연간총매출_만원']
        
        # 전년 대비 성장률(YoY) 계산
        yearly_df['성장률(%)'] = yearly_df['연간총매출_만원'].pct_change() * 100
        
        col_chart, col_data = st.columns([7, 3])
        
        with col_chart:
            fig_year = px.bar(yearly_df, x='연도', y='연간총매출_만원',
                              text_auto=',.0f', title="연도별 총 매출 규모")
            fig_year.update_traces(marker_color='#007BFF', textposition='outside')
            fig_year.update_layout(xaxis=dict(type='category'), yaxis_title="매출액 (만원)")
            st.plotly_chart(fig_year, use_container_width=True)
            
        with col_data:
            st.write("#### 연도별 실적 요약")
            yearly_disp = yearly_df.copy()
            # 포맷 변경
            yearly_disp['연간매출'] = yearly_disp['연간총매출_만원'].apply(lambda x: f"{x:,.0f} 만원")
            yearly_disp['YoY'] = yearly_disp['성장률(%)'].apply(lambda x: f"{x:+.1f}%" if pd.notnull(x) else "-")
            st.table(yearly_disp[['연도', '연간매출', 'YoY']].set_index('연도'))

    # --- 하단 상세 데이터 ---
    with st.expander("📝 전체 데이터 시트 확인 (단위: 만원)"):
        st.dataframe(df[['날짜'] + platforms_man + ['월간총매출_만원']].sort_values('날짜', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
    st.info("파일명이 '오픈마켓 매출.csv'인지 확인해 주세요.")
