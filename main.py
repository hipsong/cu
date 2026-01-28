import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정 (최상단 고정)
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
    
    # 단위 변환: 만원
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

    # --- 사이드바 내비게이션 ---
    st.sidebar.title("🏥 CU메디칼 분석 메뉴")
    menu = st.sidebar.selectbox(
        "보고 싶은 리포트를 선택하세요",
        ["🏠 전체 요약 및 상세 추이", 
         "📊 25년 플랫폼별 총매출", 
         "📈 22~25년 월별 총매출 추이", 
         "📅 22~25년 연도별 총매출"]
    )

    st.title(f"{menu}")
    st.caption("모든 수치 단위: 만원")

    # --- [기능 1] 전체 요약 및 상세 추이 (기존 틀) ---
    if menu == "🏠 전체 요약 및 상세 추이":
        col1, col2, col3 = st.columns(3)
        col1.metric("누적 총 매출", f"{df['총매출_만원'].sum()/10000:.2f} 억")
        col2.metric("최고 월 매출", f"{df['총매출_만원'].max():,.0f} 만원")
        col3.metric("운영 플랫폼", f"{len(platforms)}개")
        
        st.divider()
        selected_p = st.multiselect("비교 플랫폼 선택", platforms, default=platforms)
        selected_p_man = [f"{p}_만원" for p in selected_p]
        
        if selected_p_man:
            fig_line = px.line(df, x='날짜', y=selected_p_man, markers=True, labels=display_map)
            fig_line.update_layout(yaxis=dict(tickformat=",.0f", ticksuffix=" 만"), hovermode="x unified")
            st.plotly_chart(fig_line, use_container_width=True)

    # --- [기능 2] 25년 플랫폼별 총매출 ---
    elif menu == "📊 25년 플랫폼별 총매출":
        df_25 = df[df['연도'] == 2025]
        if df_25.empty:
            st.info("데이터에 2025년 실적이 존재하지 않습니다.")
        else:
            p_sum_25 = df_25[platforms_man].sum().sort_values(ascending=False)
            
            c1, c2 = st.columns([6, 4])
            with c1:
                st.write("#### 🏆 2025년 플랫폼 매출 비중")
                fig_pie_25 = px.pie(values=p_sum_25.values, names=[display_map[k] for k in p_sum_25.index], hole=0.4)
                fig_pie_25.update_traces(textinfo='percent+label', hovertemplate="%{value:,.0f} 만원")
                st.plotly_chart(fig_pie_25, use_container_width=True)
            with c2:
                st.write("#### 🔢 플랫폼별 합계 (만원)")
                sum_df_25 = p_sum_25.reset_index()
                sum_df_25.columns = ['플랫폼', '매출액']
                sum_df_25['플랫폼'] = sum_df_25['플랫폼'].replace(display_map)
                st.dataframe(sum_df_25.style.format({'매출액': '{:,.0f}'}), use_container_width=True)

    # --- [기능 3] 22~25년 월별 총매출 추이 ---
    elif menu == "📈 22~25년 월별 총매출 추이":
        st.write("#### 🗓️ 전사 통합 월별 매출 성장 곡선")
        fig_monthly = px.area(df, x='날짜', y='총매출_만원', title="2022년 - 2025년 전체 월 매출")
        fig_monthly.update_traces(line_color='#FF4B4B', fillcolor='rgba(255, 75, 75, 0.2)')
        fig_monthly.update_layout(yaxis=dict(tickformat=",.0f"), hovermode="x unified")
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        st.write("#### 📊 월별 매출 데이터 데이터셋")
        st.dataframe(df[['날짜', '총매출_만원']].sort_values('날짜', ascending=False), use_container_width=True)

    # --- [기능 4] 22~25년 연도별 총매출 ---
    elif menu == "📅 22~25년 연도별 총매출":
        # 22~25년 데이터 그룹화
        yearly_df = df[df['연도'].isin([2022, 2023, 2024, 2025])].groupby('연도')['총매출_만원'].sum().reset_index()
        
        col_y1, col_y2 = st.columns([7, 3])
        with col_y1:
            st.write("#### 📅 연도별 매출 총합 비교")
            fig_year = px.bar(yearly_df, x='연도', y='총매출_만원', text_auto=',.0f', color='총매출_만원', color_continuous_scale='Viridis')
            fig_year.update_layout(xaxis=dict(type='category'), yaxis_title="매출액 (만원)")
            st.plotly_chart(fig_year, use_container_width=True)
        with col_y2:
            st.write("#### 📝 연간 성장률")
            yearly_df['성장률(YoY)'] = yearly_df['총매출_만원'].pct_change() * 100
            yearly_df['매출액'] = yearly_df['총매출_만원'].map('{:,.0f} 만원'.format)
            st.table(yearly_df[['연도', '매출액']].set_index('연도'))

except Exception as e:
    st.error(f"데이터 로딩 중 오류 발생: {e}")
