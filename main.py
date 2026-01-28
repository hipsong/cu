import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="cu메디칼 오픈마켓 매출 분석", layout="wide")

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
    
    for col in numeric_cols:
        df[f"{col}_만원"] = df[col] / 10_000
        
    df['총매출_만원'] = df[numeric_cols].sum(axis=1) / 10_000
    df['연도'] = df['날짜'].dt.year
    df['월'] = df['날짜'].dt.month
    
    return df, numeric_cols.tolist()

try:
    df, platforms = load_and_clean_data()
    platforms_man = [f"{p}_만원" for p in platforms]
    display_map = {f"{p}_만원": p for p in platforms}

    # --- 사이드바 메뉴 구성 ---
    st.sidebar.title("📊 분석 메뉴")
    menu = st.sidebar.radio(
        "확인할 분석 항목을 선택하세요:",
        ["1. 플랫폼별 매출 (2025년)", "2. 월별 총매출 추이 (22~25년)", "3. 연도별 총매출 (22~24년)"]
    )

    st.title(f"🏥 {menu}")
    st.caption("단위: 만원 (KRW 10,000)")

    # --- 1. 25년 플랫폼별 총매출 ---
    if menu == "1. 플랫폼별 매출 (2025년)":
        df_25 = df[df['연도'] == 2025]
        
        if df_25.empty:
            st.warning("데이터에 2025년 실적이 아직 존재하지 않습니다.")
        else:
            col1, col2 = st.columns([6, 4])
            with col1:
                st.write("#### 🏆 2025년 플랫폼별 점유율")
                pie_25 = df_25[platforms_man].sum()
                fig_pie = px.pie(values=pie_25.values, names=[display_map[k] for k in pie_25.index],
                                 hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
                fig_pie.update_traces(textinfo='percent+label', hovertemplate="%{value:,.0f} 만원")
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.write("#### 📊 2025년 매출 순위")
                rank_25 = pie_25.sort_values(ascending=True)
                fig_bar_25 = px.bar(x=rank_25.values, y=[display_map[k] for k in rank_25.index], 
                                    orientation='h', text_auto=',.0f')
                st.plotly_chart(fig_bar_25, use_container_width=True)

    # --- 2. 22~25년 월별 총매출 추이 ---
    elif menu == "2. 월별 총매출 추이 (22~25년)":
        st.write("#### 🗓️ 전사 통합 월별 매출 흐름")
        
        # 전체 통합 라인 차트
        fig_monthly = px.line(df, x='날짜', y='총매출_만원', markers=True,
                              title="2022년 - 2025년 월간 총매출 변동")
        fig_monthly.update_traces(line_color='#FF4B4B', fill='tozeroy')
        fig_monthly.update_layout(yaxis=dict(tickformat=",.0f", ticksuffix=" 만"), hovermode="x unified")
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        # 시즌성 분석을 위한 연도별 비교 차트
        st.write("#### 💡 전년 대비 월별 성장 비교")
        df['월_문자'] = df['월'].apply(lambda x: f"{x}월")
        fig_compare = px.line(df, x='월_문자', y='총매출_만원', color='연도',
                             markers=True, title="연도별 동일 월 매출 비교")
        st.plotly_chart(fig_compare, use_container_width=True)

    # --- 3. 22~24년 연도별 총매출 ---
    elif menu == "3. 연도별 총매출 (22~24년)":
        # 22~24년 데이터만 필터링
        df_target_years = df[df['연도'].isin([2022, 2023, 2024])]
        yearly_summary = df_target_years.groupby('연도')['총매출_만원'].sum().reset_index()
        
        col1, col2 = st.columns([7, 3])
        
        with col1:
            st.write("#### 📅 연도별 매출 총합")
            fig_year = px.bar(yearly_summary, x='연도', y='총매출_만원', 
                              text_auto=',.1f', color='연도',
                              title="2022 - 2024 전사 실적 합계")
            fig_year.update_layout(xaxis=dict(type='category'), yaxis_title="매출액 (만원)")
            st.plotly_chart(fig_year, use_container_width=True)
            
        with col2:
            st.write("#### 📝 실적 요약표")
            yearly_summary['매출액'] = yearly_summary['총매출_만원'].map('{:,.0f} 만원'.format)
            # 전년 대비 성장률 계산
            yearly_summary['성장률(YoY)'] = yearly_summary['총매출_만원'].pct_change() * 100
            yearly_summary['성장률(YoY)'] = yearly_summary['성장률(YoY)'].apply(lambda x: f"{x:+.1f}%" if pd.notnull(x) else "-")
            st.table(yearly_summary[['연도', '매출액', '성장률(YoY)']].set_index('연도'))

    st.divider()
    # 하단 데이터 익스팬더 유지
    with st.expander("📝 전체 데이터 시트 보기"):
        st.dataframe(df[['날짜'] + platforms_man + ['총매출_만원']].sort_values('날짜', ascending=False))

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
    st.info("파일명이 '오픈마켓 매출.csv'인지 확인해 주세요.")
