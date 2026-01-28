import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="회사 매출 분석 시스템", layout="wide")

@st.cache_data
def load_and_clean_data():
    file_path = '오픈마켓 매출.csv'
    try:
        df = pd.read_csv(file_path, encoding='cp949')
    except:
        df = pd.read_csv(file_path, encoding='utf-8-sig')

    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['날짜'] = pd.to_datetime(df['날짜'])
    
    # 숫자형 데이터 정제
    numeric_cols = df.columns.drop('날짜')
    for col in numeric_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # 단위 변환: 만원
    for col in numeric_cols:
        df[f"{col}_만원"] = df[col] / 10_000
        
    df['월간총매출_만원'] = df[numeric_cols].sum(axis=1) / 10_000
    
    # 연도별 합계를 위한 연도 컬럼 추가
    df['연도'] = df['날짜'].dt.year
    
    return df, numeric_cols.tolist()

try:
    df, platforms = load_and_clean_data()
    platforms_man = [f"{p}_만원" for p in platforms]
    display_map = {f"{p}_만원": p for p in platforms}

    st.title("🏢 전사 매출 분석 대시보드")
    
    # 상단 요약 KPI (최근 월매출 삭제, 총 누적과 최고 기록 중심)
    c1, c2, c3 = st.columns(3)
    c1.metric("총 누적 매출액", f"{df['월간총매출_만원'].sum()/10000:.2f} 억 원")
    c2.metric("최고 월 매출액", f"{df['월간총매출_만원'].max():,.0f} 만원")
    c3.metric("데이터 집계 기간", f"{df['날짜'].min().year} ~ {df['날짜'].max().year}")

    st.divider()

    # --- 매출 추이 분석 섹션 ---
    tab1, tab2 = st.tabs(["📅 월간 매출 추이", "📅 연간 매출 추이"])

    with tab1:
        st.subheader("회사의 월별 총 매출 흐름")
        # 전체 합계 라인 차트
        fig_month = px.line(df, x='날짜', y='월간총매출_만원', 
                            markers=True, line_shape='spline',
                            title="전체 플랫폼 통합 월 매출 추이")
        fig_month.update_traces(line_color='#FF4B4B', fill='tozeroy') # 강조색 및 영역 채우기
        fig_month.update_layout(yaxis_title="매출액 (만원)", yaxis=dict(tickformat=",.0f"))
        st.plotly_chart(fig_month, use_container_width=True)
        
        # 플랫폼별 스택(Stack) 차트 추가 (비중 확인용)
        st.write("#### 플랫폼별 기여도 포함 추이")
        fig_stack = px.area(df, x='날짜', y=platforms_man, labels=display_map,
                            color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_stack.update_layout(yaxis_title="매출액 (만원)", hovermode="x unified")
        st.plotly_chart(fig_stack, use_container_width=True)

    with tab2:
        st.subheader("연도별 총 성과 분석")
        # 연도별 그룹화 계산
        yearly_df = df.groupby('연도')['월간총매출_만원'].sum().reset_index()
        yearly_df.columns = ['연도', '연간총매출_만원']
        
        col_chart, col_data = st.columns([7, 3])
        
        with col_chart:
            fig_year = px.bar(yearly_df, x='연도', y='연간총매출_만원',
                              text_auto=',.0f', title="연도별 총 매출액 (만원)")
            fig_year.update_traces(marker_color='#007BFF')
            fig_year.update_layout(xaxis=dict(type='category'), yaxis_title="매출액 (만원)")
            st.plotly_chart(fig_year, use_container_width=True)
            
        with col_data:
            st.write("#### 연도별 요약 표")
            yearly_disp = yearly_df.copy()
            yearly_disp['연간총매출_만원'] = yearly_disp['연간총매출_만원'].map('{:,.0f} 만원'.format)
            st.table(yearly_disp.set_index('연도'))

    # --- 하단 상세 데이터 ---
    with st.expander("📝 원본 데이터 상세 확인"):
        st.dataframe(df[['날짜'] + platforms_man + ['월간총매출_만원']].sort_values('날짜', ascending=False))

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
    st.info("파일명이 '오픈마켓 매출.csv'인지 확인해 주세요.")
