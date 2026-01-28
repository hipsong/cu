import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정 (다크모드/라이트모드 모두 대응 가능한 레이아웃)
st.set_page_config(page_title="오픈마켓 매출 분석 대시보드", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def load_and_clean_data():
    file_path = '오픈마켓 매출.csv'
    try:
        df = pd.read_csv(file_path, encoding='cp949')
    except:
        df = pd.read_csv(file_path, encoding='utf-8-sig')

    # 'Unnamed' 열 제거 및 전처리
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['날짜'] = pd.to_datetime(df['날짜'])
    
    # 데이터 정제 (숫자형 변환 및 결측치 처리)
    numeric_cols = df.columns.drop('날짜')
    for col in numeric_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    df['총매출'] = df[numeric_cols].sum(axis=1)
    return df, numeric_cols.tolist()

try:
    df, platforms = load_and_clean_data()

    # --- 사이드바: 필터 및 옵션 ---
    with st.sidebar:
        st.header("📊 분석 설정")
        selected_p = st.multiselect("분석할 플랫폼", platforms, default=platforms)
        st.divider()
        chart_type = st.radio("그래프 타입 선택", ["라인 차트 (흐름)", "영역 차트 (누적 비중)"])
        st.info("Tip: 그래프의 특정 범례를 더블클릭하면 해당 항목만 볼 수 있습니다.")

    # --- 메인 타이틀 ---
    st.title("📈 오픈마켓 채널별 매출 분석")
    st.caption(f"데이터 기준: {df['날짜'].min().strftime('%Y-%m')} ~ {df['날짜'].max().strftime('%Y-%m')}")

    # --- 핵심 지표 (KPI Cards) ---
    latest_sales = df['총매출'].iloc[-1]
    prev_sales = df['총매출'].iloc[-2]
    growth_rate = ((latest_sales - prev_sales) / prev_sales) * 100

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("총 누적 매출", f"{df['총매출'].sum():,.0f}원")
    m2.metric("최근 월 매출", f"{latest_sales:,.0f}원", f"{growth_rate:.1f}%")
    m3.metric("최고 매출 기록", f"{df['총매출'].max():,.0f}원")
    m4.metric("운영 채널 수", f"{len(platforms)}개")

    st.divider()

    # --- 메인 시각화 섹션 ---
    if selected_p:
        c1, c2 = st.columns([7, 3])

        with c1:
            st.subheader("🗓️ 매출 추이 분석")
            if chart_type == "라인 차트 (흐름)":
                fig = px.line(df, x='날짜', y=selected_p, markers=True,
                              color_discrete_sequence=px.colors.qualitative.Pastel)
            else:
                fig = px.area(df, x='날짜', y=selected_p,
                              color_discrete_sequence=px.colors.qualitative.Safe)
            
            fig.update_layout(
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("🥧 채널 점유율")
            pie_data = df[selected_p].sum()
            fig_pie = px.pie(values=pie_data.values, names=pie_data.index, 
                             hole=0.5, color_discrete_sequence=px.colors.qualitative.Set3)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

        # --- 플랫폼별 평균 성과 비교 (하단) ---
        st.subheader("📊 플랫폼별 월 평균 매출 비교")
        avg_sales = df[selected_p].mean().sort_values(ascending=False)
        fig_bar = px.bar(x=avg_sales.index, y=avg_sales.values, 
                         color=avg_sales.index, text_auto='.2s',
                         labels={'x': '플랫폼', 'y': '평균 매출'})
        st.plotly_chart(fig_bar, use_container_width=True)

    else:
        st.warning("분석할 플랫폼을 하나 이상 선택해 주세요.")

    # --- 데이터 확인 ---
    with st.expander("📁 전체 데이터 시트 확인"):
        st.dataframe(df.sort_values('날짜', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
