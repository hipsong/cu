import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="오픈마켓 매출 분석", layout="wide")

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
    
    # --- [수정 포인트] 단위 변환: 원 -> 백만 원 ---
    for col in numeric_cols:
        df[f"{col}_백만"] = df[col] / 1_000_000
        
    df['총매출'] = df[numeric_cols].sum(axis=1)
    df['총매출_백만'] = df['총매출'] / 1_000_000
    
    return df, numeric_cols.tolist()

try:
    df, platforms = load_and_clean_data()
    # 그래프에 사용할 컬럼 리스트 (백만 단위 컬럼들)
    platforms_million = [f"{p}_백만" for p in platforms]
    # 표시용 이름 맵핑 (컬럼명에서 '_백만' 제거하고 보여주기 위함)
    name_map = {f"{p}_백만": p for p in platforms}

    st.title("📊 오픈마켓 매출 분석 (단위: 백만 원)")
    
    # --- 상단 지표 ---
    m1, m2, m3 = st.columns(3)
    m1.metric("총 누적 매출", f"{df['총매출'].sum()/100000000:.1f} 억 원")
    m2.metric("최근 월 매출", f"{df['총매출'].iloc[-1]/1000000:.1f} 백만 원")
    m3.metric("최고 매출 월", df.loc[df['총매출'].idxmax(), '날짜'].strftime('%Y-%m'))

    st.divider()

    # --- 메인 그래프 섹션 ---
    selected_p_raw = st.multiselect("플랫폼 선택", platforms, default=platforms)
    selected_p_million = [f"{p}_백만" for p in selected_p_raw]

    if selected_p_million:
        # 차트 생성
        fig = px.line(df, x='날짜', y=selected_p_million, markers=True,
                      labels=name_map, # 범례 이름을 원래 이름으로 변경
                      title="월별 매출 추이 (단위: 백만 원)")

        # --- [수정 포인트] 그래프 수치 포맷팅 ---
        fig.update_traces(
            hovertemplate="<b>%{secondary_y}</b><br>날짜: %{x}<br>매출: %{y:.1f} 백만 원<extra></extra>"
        )
        
        fig.update_layout(
            yaxis_title="매출액 (백만 원)",
            yaxis=dict(ticksuffix=" 백만"), # 축 옆에 '백만' 표시
            hovermode="x unified",
            legend_title="플랫폼",
            legend=dict(orientation="h", y=1.1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # --- 하단 점유율 차트 ---
        st.subheader("🥧 누적 점유율")
        pie_data = df[selected_p_million].sum()
        fig_pie = px.pie(values=pie_data.values, names=[name_map[n] for n in pie_data.index], 
                         hole=0.4)
        fig_pie.update_traces(textinfo='percent+label', hovertemplate="%{label}: %{value:.1f} 백만 원")
        st.plotly_chart(fig_pie, use_container_width=True)

    # 데이터 표
    with st.expander("원본 데이터 시트 (단위: 원)"):
        st.dataframe(df[['날짜'] + platforms + ['총매출']])

except Exception as e:
    st.error(f"오류 발생: {e}")
