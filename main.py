import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
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
    df['연도'] = df['날짜'].dt.year
    
    return df, numeric_cols.tolist()

try:
    df, platforms = load_and_clean_data()
    platforms_man = [f"{p}_만원" for p in platforms]
    display_map = {f"{p}_만원": p for p in platforms}

    st.title("🏥 CU메디컬 채널별 성과 및 추이 대시보드")
    
    # --- 상단 탭 구성 ---
    tab_total, tab_platform, tab_yearly = st.tabs(["📊 월별 전사 추이", "📱 플랫폼별 분석", "📅 연도별 성과"])

    # --- [탭 1] 월별 전사 추이 ---
    with tab_total:
        st.subheader("🗓️ 회사의 전체 월간 매출 추이")
        fig_total = px.area(df, x='날짜', y='월간총매출_만원', 
                            title="전체 플랫폼 합산 매출 흐름 (만원)")
        fig_total.update_layout(yaxis_title="매출액 (만원)", yaxis=dict(tickformat=",.0f"), hovermode="x unified")
        st.plotly_chart(fig_total, use_container_width=True)
        
        # 지표 요약
        m1, m2 = st.columns(2)
        m1.metric("최고 월 매출액", f"{df['월간총매출_만원'].max():,.0f} 만원")
        m2.metric("평균 월 매출액", f"{df['월간총매출_만원'].mean():,.0f} 만원")

    # --- [탭 2] 플랫폼별 분석 ---
    with tab_platform:
        st.subheader("📱 개별 플랫폼 성과 확인")
        target_p = st.selectbox("분석할 플랫폼을 선택하세요", platforms)
        
        col_p1, col_p2 = st.columns([7, 3])
        
        with col_p1:
            fig_p = px.line(df, x='날짜', y=f"{target_p}_만원", markers=True,
                            title=f"[{target_p}] 채널 매출 추이")
            fig_p.update_layout(yaxis_title="매출액 (만원)", yaxis=dict(tickformat=",.0f"))
            st.plotly_chart(fig_p, use_container_width=True)
            
        with col_p2:
            st.write(f"#### {target_p} 데이터 요약")
            p_sum = df[f"{target_p}_만원"].sum()
            p_avg = df[f"{target_p}_만원"].mean()
            p_share = (p_sum / df['월간총매출_만원'].sum()) * 100
            
            st.info(f"""
            - **누적 매출:** {p_sum:,.0f} 만원
            - **월 평균:** {p_avg:,.0f} 만원
            - **전체 비중:** {p_share:.1f}%
            """)

    # --- [탭 3] 연도별 성과 ---
    with tab_yearly:
        st.subheader("📅 연도별 매출 총결산")
        yearly_df = df.groupby('연도')['월간총매출_만원'].sum().reset_index()
        
        # 연도별 플랫폼 상세 합계
        yearly_platforms = df.groupby('연도')[platforms_man].sum()
        yearly_platforms.columns = platforms # '_만원' 제거

        col_y1, col_y2 = st.columns([6, 4])
        
        with col_y1:
            fig_y = px.bar(yearly_df, x='연도', y='월간총매출_만원', text_auto=',.0f',
                           title="연도별 전사 매출 총합")
            fig_y.update_layout(xaxis=dict(type='category'), yaxis_title="매출액 (만원)")
            st.plotly_chart(fig_y, use_container_width=True)
            
        with col_y2:
            st.write("#### 연도별 플랫폼별 매출액")
            st.dataframe(yearly_platforms.style.format("{:,.0f}"))

    st.divider()
    # 원본 데이터 시트
    with st.expander("📝 전체 데이터 시트 보기"):
        st.dataframe(df[['날짜'] + platforms_man + ['월간총매출_만원']].sort_values('날짜', ascending=False))

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
