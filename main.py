import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="cu메디컬 오픈마켓 매출 분석", layout="wide")

@st.cache_data
def load_and_clean_data():
    # 요청하신 대로 파일명 변경
    file_path = '오픈마켓 매출.csv'
    try:
        df = pd.read_csv(file_path, encoding='cp949')
    except:
        df = pd.read_csv(file_path, encoding='utf-8-sig')

    # 불필요한 Unnamed 열 제거
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['날짜'] = pd.to_datetime(df['날짜'])
    
    # 숫자형 데이터 정제 (콤마 제거 및 float 변환)
    numeric_cols = df.columns.drop('날짜')
    for col in numeric_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # --- 만원 단위 변환 로직 ---
    for col in numeric_cols:
        df[f"{col}_만원"] = df[col] / 10_000
        
    df['총매출_만원'] = df[numeric_cols].sum(axis=1) / 10_000
    
    return df, numeric_cols.tolist()

try:
    df, platforms = load_and_clean_data()
    # 만원 단위 컬럼 매핑
    platforms_man = [f"{p}_만원" for p in platforms]
    display_map = {f"{p}_만원": p for p in platforms}

    # 헤더 섹션
    st.title("📈 매출 성과 분석 대시보드")
    st.subheader(f"📊 단위: 만원 (KRW 10,000)")
    
    # KPI 지표 (상단 카드)
    total_sales_man = df['총매출_만원'].sum()
    latest_sales_man = df['총매출_만원'].iloc[-1]
    prev_sales_man = df['총매출_만원'].iloc[-2]
    growth = ((latest_sales_man - prev_sales_man) / prev_sales_man) * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("누적 총 매출", f"{total_sales_man/10000:.2f} 억")
    col2.metric("최근 월 매출", f"{latest_sales_man:,.0f} 만원", f"{growth:.1f}%")
    col3.metric("최고 월 매출", f"{df['총매출_만원'].max():,.0f} 만원")
    col4.metric("운영 채널", f"{len(platforms)}개")

    st.divider()

    # 메인 분석 영역
    selected_p = st.multiselect("비교 플랫폼 선택", platforms, default=platforms)
    selected_p_man = [f"{p}_만원" for p in selected_p]

    if selected_p_man:
        # 1. 시계열 추이 그래프
        fig_line = px.line(df, x='날짜', y=selected_p_man, markers=True,
                           labels=display_map,
                           title="플랫폼별 월간 매출 추이 (만원)")
        
        fig_line.update_layout(
            yaxis=dict(tickformat=",.0f", ticksuffix=" 만"),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_line.update_traces(hovertemplate="%{y:,.0f} 만원")
        st.plotly_chart(fig_line, use_container_width=True)

        # 2. 하단 상세 분석 (비중 및 평균)
        c1, c2 = st.columns(2)
        
        with c1:
            st.write("### 🥧 플랫폼별 누적 비중")
            pie_values = df[selected_p_man].sum()
            fig_pie = px.pie(values=pie_values, names=[display_map[k] for k in pie_values.index],
                             hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_pie.update_traces(textinfo='percent+label', hovertemplate="%{value:,.0f} 만원")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with c2:
            st.write("### 📊 플랫폼별 월 평균 매출")
            avg_val = df[selected_p_man].mean().sort_values()
            fig_bar = px.bar(x=avg_val.values, y=[display_map[k] for k in avg_val.index], 
                             orientation='h', text_auto=',.0f')
            fig_bar.update_layout(xaxis_title="평균 매출 (만원)", yaxis_title="")
            st.plotly_chart(fig_bar, use_container_width=True)

    # 데이터 테이블
    with st.expander("📝 전체 데이터 시트 (만원 단위)"):
        st.dataframe(df[['날짜'] + selected_p_man + ['총매출_만원']].sort_values('날짜', ascending=False))

except Exception as e:
    st.error(f"파일을 찾을 수 없거나 데이터 오류가 발생했습니다: {e}")
    st.info("파일명이 '오픈마켓 매출.csv'인지 확인해 주세요.")
