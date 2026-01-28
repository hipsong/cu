import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="오픈마켓 매출 분석 대시보드", layout="wide")

# 데이터 로드 함수 수정 (인코딩 문제 해결)
@st.cache_data
def load_data():
    file_path = '오픈마켓 매출.csv'
    try:
        # 먼저 cp949(엑셀 기본)로 시도
        df = pd.read_csv(file_path, encoding='cp949')
    except:
        # 안되면 euc-kr로 시도
        df = pd.read_csv(file_path, encoding='euc-kr')
        
    df['날짜'] = pd.to_datetime(df['날짜'])
    # 숫자 데이터 내 콤마(,) 제거 및 수치화 (혹시 모를 에러 방지)
    for col in df.columns[1:]:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)
            
    df['총매출'] = df.iloc[:, 1:].sum(axis=1)
    return df

try:
    df = load_data()

    st.title("📊 오픈마켓 매출 성과 분석")
    st.markdown(f"**데이터 기간:** {df['날짜'].min().strftime('%Y-%m')} ~ {df['날짜'].max().strftime('%Y-%m')}")

    # --- KPI 지표 ---
    col1, col2, col3, col4 = st.columns(4)
    total_sales = df['총매출'].sum()
    last_month_sales = df['총매출'].iloc[-1]
    prev_month_sales = df['총매출'].iloc[-2]
    mom_growth = (last_month_sales - prev_month_sales) / prev_month_sales * 100

    col1.metric("누적 총 매출", f"{total_sales:,.0f}원")
    col2.metric("최근 월 매출", f"{last_month_sales:,.0f}원", f"{mom_growth:.1f}%")
    col3.metric("플랫폼 수", f"{len(df.columns)-2}개")
    col4.metric("최고 매출액", f"{df['총매출'].max():,.0f}원")

    st.divider()

    # --- 매출 추이 그래프 ---
    st.subheader("📈 월별 매출 성장 추이")
    
    # 멀티 셀렉트 (플랫폼 선택)
    platforms = df.columns[1:-1].tolist()
    selected = st.multiselect("확인할 플랫폼을 선택하세요", platforms, default=platforms)
    
    fig_line = px.line(df, x='날짜', y=selected, markers=True,
                      title="플랫폼별 매출 변화 (월간)")
    fig_line.update_layout(hovermode="x unified")
    st.plotly_chart(fig_line, use_container_width=True)

    # --- 분석 대시보드 하단 ---
    c1, c2 = st.columns([6, 4])
    
    with c1:
        st.subheader("🛶 시장 점유율 (누적 비중)")
        platform_sums = df[platforms].sum().sort_values(ascending=True)
        fig_bar = px.bar(x=platform_sums.values, y=platform_sums.index, orientation='h',
                        labels={'x':'매출 총합', 'y':'플랫폼'},
                        color=platform_sums.values, color_continuous_scale='Viridis')
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("🎯 플랫폼별 기여도")
        fig_pie = px.pie(names=platform_sums.index, values=platform_sums.values, hole=0.5)
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- 데이터 분석 리포트 자동 생성 ---
    st.divider()
    st.subheader("📝 데이터 분석 요약")
    best_platform = platform_sums.index[-1]
    st.info(f"""
    1. **주력 채널:** 현재 가장 매출 기여도가 높은 채널은 **{best_platform}**입니다.
    2. **성장세:** 전체 매출은 시간의 흐름에 따라 변화하고 있으며, 최근 월 매출은 전월 대비 {mom_growth:.1f}% 변화했습니다.
    3. **제언:** 매출 변동성이 큰 플랫폼의 마케팅 집행 시기를 데이터의 피크 지점과 비교해 분석할 필요가 있습니다.
    """)

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
    st.warning("CSV 파일을 메모장으로 열어 '다른 이름으로 저장'할 때 인코딩을 'UTF-8'로 설정하여 다시 저장해 보세요.")

