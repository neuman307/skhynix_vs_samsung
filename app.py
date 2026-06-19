import streamlit as st
import plotly.graph_objects as go

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="삼성전자 vs SK하이닉스 시총 비교", page_icon="📊", layout="centered"
)

st.title("📊 삼성전자 vs SK하이닉스 시총 비교 분석")
st.markdown("---")

# 2. 사이드바에서 데이터 입력 받기 (기본값 설정)
st.sidebar.header("⚙️ 시가총액 데이터 입력")

samsung_cap = st.sidebar.number_input(
    "삼성전자 시가총액 (억원)",
    min_value=1,
    value=2154353,  # 기본값
    step=1000,
    format="%d",
)

hynix_cap = st.sidebar.number_input(
    "SK하이닉스 시가총액 (억원)",
    min_value=1,
    value=2000000,  # 기본값
    step=1000,
    format="%d",
)

# 3. 데이터 계산
percentage = (hynix_cap / samsung_cap) * 100

# 4. 메인 화면에 대시보드 카드 배치
col1, col2 = st.columns(2)

with col1:
    st.metric(label="삼성전자 시가총액", value=f"{samsung_cap:,} 억 원")

with col2:
    st.metric(
        label="SK하이닉스 시가총액",
        value=f"{hynix_cap:,} 억 원",
        delta=f"삼성 대비 {percentage:.2f}%",
    )

st.markdown("---")

# 5. 하이라이트 결과창
st.subheader("💡 분석 결과")
st.info(
    f"현재 **SK하이닉스**의 시가총액은 **삼성전자** 대비 **{percentage:.2f}%** 수준입니다."
)

# 6. Plotly를 활용한 시각화 차트
fig = go.Figure(
    go.Bar(
        x=["삼성전자", "SK하이닉스"],
        y=[samsung_cap, hynix_cap],
        marker_color=["#0A47A3", "#FF6C00"],  # 기업 고유 컬러 반영
        text=[f"{samsung_cap:,}억", f"{hynix_cap:,}억"],
        textposition="auto",
    )
)

fig.update_layout(
    title="시가총액 비교 그래프 (단위: 억 원)",
    xaxis_title="기업명",
    yaxis_title="시가총액",
    template="plotly_white",
)

st.plotly_chart(fig, use_container_width=True)
