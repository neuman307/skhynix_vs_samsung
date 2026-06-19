import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 페이지 기본 설정
st.set_page_config(page_title="실시간 시총 비교", page_icon="📊", layout="centered")

st.title("📊 실시간 삼성전자 vs SK하이닉스 시총 비교")
st.write("yfinance 패키지를 통해 실제 주가 데이터를 받아와 5초마다 자동 갱신합니다.")
st.markdown("---")

# 5초마다 이 안의 코드만 재실행 (st.fragment)
@st.fragment(run_every=5)
def render_dashboard():
    try:
        # 발행주식수 (보통주 기준 고정값 세팅)
        samsung_shares = 5969782550
        hynix_shares = 728002365

        # yfinance를 통해 오늘 하루치 주가 데이터를 가장 빠르게 조회
        samsung_data = yf.Ticker("005930.KS").history(period="1d")
        hynix_data = yf.Ticker("000660.KS").history(period="1d")

        if samsung_data.empty or hynix_data.empty:
            st.warning("데이터를 불러오지 못했습니다. 장이 열리지 않은 시간이거나 API 지연일 수 있습니다.")
            return

        # 가장 최근 종가(현재가) 추출
        samsung_price = int(samsung_data['Close'].iloc[-1])
        hynix_price = int(hynix_data['Close'].iloc[-1])

        # 시가총액 계산 (주식수 * 현재가 / 1조)
        # 소수점까지 깔끔하게 계산하기 위해 float(실수) 형태로 유지합니다.
        samsung_cap = (samsung_price * samsung_shares) / 1000000000000
        hynix_cap = (hynix_price * hynix_shares) / 1000000000000
        
        # 비율 계산
        percentage = (hynix_cap / samsung_cap) * 100

        # 메인 카드 UI 출력
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label="삼성전자 (현재가 / 시총)", 
                value=f"{samsung_price:,} 원", 
                # 소수점 첫째 자리까지 조 단위 표기
                delta=f"{samsung_cap:,.1f} 조 원" 
            )
        with col2:
            st.metric(
                label="SK하이닉스 (현재가 / 시총)", 
                value=f"{hynix_price:,} 원", 
                delta=f"삼성 대비 {percentage:.2f}%",
                delta_color="inverse" if percentage < 90 else "normal"
            )

        st.markdown("---")
        st.info(f"⏱️ 실시간 시장 데이터 연동 중... 현재 시총 비율은 **{percentage:.2f}%** 입니다.")

        # Plotly 차트 출력
        fig = go.Figure(
            go.Bar(
                x=["삼성전자", "SK하이닉스"],
                y=[samsung_cap, hynix_cap],
                marker_color=["#0A47A3", "#FF6C00"],
                # 그래프 위 텍스트도 조 단위로 변경
                text=[f"{samsung_cap:,.1f}조", f"{hynix_cap:,.1f}조"], 
                textposition="auto",
            )
        )
        fig.update_layout(
            title="실시간 시가총액 비교 (단위: 조 원)",
            xaxis_title="기업명",
            yaxis_title="시가총액",
            template="plotly_white",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")

# 앱 실행
render_dashboard()
