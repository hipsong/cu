import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 설정
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
    
    # 만원 단위 변환
    for col in numeric_cols:
        df[f"{col}_만원"] = df[col] / 10_000
        
    df['총매출_만원'] = df[numeric_cols].sum(axis=1) / 10_000
    df['연도'] = df['날짜'].dt.year
    
    return df, numeric_cols.tolist()

try:
    df, platforms = load_and_clean_data()
    platforms_man = [f"{p}_만원" for p in platforms]
    display_map = {f"{p}_만원": p for p in platforms}

    # 헤더 섹션
    st.title("📈 매출 성과 분석")
    st.subheader(f"📊 단위: 만원 (KRW 10,000)")
    
    # KPI 지표
    total_sales_man = df['총매출_만원'].sum()
    latest_sales_man = df['총매출_만원'].iloc[-1]
    prev_sales_man = df['총매출_만원'].iloc[-2]
    growth = ((latest_sales_man - prev_sales_man) / prev_sales_man) * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("누적 총 매출", f"{total_sales_man/10000:.2f} 억")
    col2.metric("최근 월 매출", f"{latest_sales_man:,.0f} 만원", f"{growth:.1f}%")
    col3.metric("최고 월 매출", f"{df['총매출_만원'].max():,.0f} 만원")
    col4.metric("운영 플랫폼", f"{len(platforms)}개")

    st.divider()

    # --- [추가 기능] 2025년도 플랫폼별 성과 분석 ---
    st.header("🏆 2025년도 플랫폼별 성과 합계")
    df_2025 = df[df['연도'] == 2025]

    if df_2025.empty:
        st.info("현재 데이터에 2025년 실적 데이터가 없습니다.")
    else:
        # 2025년 플랫폼별 합계 계산
        sum_2025 = df_2025[platforms_man].sum().sort_values(ascending=False)
        
        c1, c2 = st.columns([6, 4])
        with c1:
            # 2025년 매출 순위 막대 그래프
            fig_25_bar = px.bar(
                x=sum_2025.values, 
                y=[display_map[k] for k in sum_2025.index],
                orientation='h',
                text_auto=',.0f',
                title="2025년 플랫폼별 누적 매출 순위",
                labels={'x': '매출액(만원)', 'y': '플랫폼'},
                color=sum_2025.values,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_25_bar, use_container_width=True)
            
        with c2:
            # 2025년 매출 비중 파이 차트
            fig_25_pie = px.pie(
                values=sum_2025.values,
                names=[display_map[k] for k in sum_2025.index],
                title="2025년 플랫폼별 매출 비중",
                hole=0.4
            )
            fig_25_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_25_pie, use_container_width=True)

    st.divider()

    # 기존 메인 분석 영역 (멀티 셀렉트 및 추이)
    st.header("📉 플랫폼별 상세 추이 비교")
    selected_p = st.multiselect("비교 플랫폼 선택", platforms, default=platforms)
    selected_p_man = [f"{p}_만원" for p in selected_p]

    if selected_p_man:
        fig_line = px.line(df, x='날짜', y=selected_p_man, markers=True,
                           labels=display_map,
                           title="전체 기간 플랫폼별 월간 매출 추이 (만원)")
        
        fig_line.update_layout(
            yaxis=dict(tickformat=",.0f", ticksuffix=" 만"),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_line.update_traces(hovertemplate="%{y:,.0f} 만원")
        st.plotly_chart(fig_line, use_container_width=True)

        # 하단 상세 분석 (비중 및 평균)
        c3, c4 = st.columns(2)
        with c3:
            st.write("### 🥧 선택 플랫폼 누적 비중 (전체)")
            pie_values = df[selected_p_man].sum()
            fig_pie = px.pie(values=pie_values, names=[display_map[k] for k in pie_values.index],
                             hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_pie.update_traces(textinfo='percent+label', hovertemplate="%{value:,.0f} 만원")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with c4:
            st.write("### 📊 선택 플랫폼 월 평균 매출 (전체)")
            avg_val = df[selected_p_man].mean().sort_values()
            fig_bar = px.bar(x=avg_val.values, y=[display_map[k] for k in avg_val.index], 
                             orientation='h', text_auto=',.0f')
            fig_bar.update_layout(xaxis_title="평균 매출 (만원)", yaxis_title="")
            st.plotly_chart(fig_bar, use_container_width=True)

    # 데이터 테이블
    with st.expander("📝 전체 데이터 시트 (만원 단위)"):
        st.dataframe(df[['날짜'] + platforms_man + ['총매출_만원']].sort_values('날짜', ascending=False))

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
