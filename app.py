import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import time

# 1. 페이지 테마 설정 및 CSS 주입
st.set_page_config(page_title="NEO-SEOUL MARKET CAP", page_icon="🧬", layout="wide")

# 사이버펑크 CSS 정의
cyberpunk_css = """
<style>
    /* 전체 배경: 어두운 그리드 패턴 */
    .stApp {
        background-color: #0d1117;
        background-image: 
            linear-gradient(rgba(10, 10, 30, 0.7) 1px, transparent 1px),
            linear-gradient(90deg, rgba(10, 10, 30, 0.7) 1px, transparent 1px);
        background-size: 50px 50px;
        color: #e0e0e0;
        font-family: 'Courier New', Courier, monospace; /* 미래지향적인 폰트 느낌 */
    }

    /* 제목: 네온 그린 & 글리치 효과 */
    .cyber-title {
        color: #39ff14; /* 네온 그린 */
        text-align: center;
        text-transform: uppercase;
        font-size: 2.8em;
        font-weight: bold;
        text-shadow: 
            0 0 5px #39ff14,
            0 0 10px #39ff14,
            0 0 20px #39ff14,
            0 0 40px #39ff14,
            0 0 80px #39ff14;
        position: relative;
        overflow: hidden;
        margin-bottom: 30px;
        letter-spacing: 2px;
    }

    /* 네온 텍스트 스타일 */
    .neon-blue { color: #00ffff; text-shadow: 0 0 5px #00ffff; }
    .neon-pink { color: #ff00ff; text-shadow: 0 0 5px #ff00ff; }
    .neon-orange { color: #ff9900; text-shadow: 0 0 5px #ff9900; }

    /* 일반 텍스트 및 안내 메시지 */
    .stAlert, .stMarkdown {
        background-color: rgba(20, 20, 40, 0.5);
        border: 1px solid #333;
        color: #aaa;
    }

    /* 메트릭 상자: 네온 테두리 */
    .stMetric {
        background-color: rgba(20, 20, 40, 0.7);
        border: 2px solid #333;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 0 15px rgba(50, 50, 100, 0.5);
        transition: border-color 0.3s;
    }

    .stMetric:hover {
        border-color: #ff00ff; /* 핑크색으로 변화 */
        box-shadow: 0 0 20px rgba(255, 0, 255, 0.7);
    }

    /* 메트릭 값: 각 기업 색상 적용 */
    .samsung-metric .stMetricValue { color: #00ffff !important; text-shadow: 0 0 10px #00ffff; }
    .hynix-metric .stMetricValue { color: #ff9900 !important; text-shadow: 0 0 10px #ff9900; }

    /* Plotly 그래프 영역: 어두운 배경 */
    .plot-container > div {
        background-color: rgba(10, 10, 20, 0.8);
        border-radius: 10px;
        border: 1px solid #333;
    }
</style>
"""

# CSS 주입
st.markdown(cyberpunk_css, unsafe_allow_html=True)

# 제목 표시
st.markdown("<div class='cyber-title'>NEO-SEOUL MARKET CAP</div>", unsafe_allow_html=True)
st.write(
    "<p style='text-align: center; color: #aaa;'>예측 불가능한 디지털 시장, 5초마다 리얼타임 데이터 동기화 중...</p>",
    unsafe_allow_html=True,
)
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
            st.warning(
                "<span class='neon-orange'>데이터 네트워크 연결 실패. 오프라인 모드일 수 있습니다.</span>",
                unsafe_allow_html=True,
            )
            return

        # 가장 최근 종가(현재가) 추출
        samsung_price = int(samsung_data["Close"].iloc[-1])
        hynix_price = int(hynix_data["Close"].iloc[-1])

        # 시가총액 계산 (주식수 * 현재가 / 1조)
        samsung_cap = (samsung_price * samsung_shares) / 1000000000000
        hynix_cap = (hynix_price * hynix_shares) / 1000000000000

        # 비율 계산
        percentage = (hynix_cap / samsung_cap) * 100

        # 메인 카드 UI 출력
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='samsung-metric'>", unsafe_allow_html=True)
            st.metric(
                label="삼성전자 (현재가 / 시총)",
                value=f"{samsung_price:,} 원",
                delta=f"{samsung_cap:,.1f} 조 원",
            )
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='hynix-metric'>", unsafe_allow_html=True)
            st.metric(
                label="SK하이닉스 (현재가 / 시총)",
                value=f"{hynix_price:,} 원",
                delta=f"{hynix_cap:,.1f} 조 원",
            )
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.info(
            f"<span class='neon-blue'>네트워크 동기화 성공.</span> 현재 시총 비율은 <span class='neon-pink'>{percentage:.2f}%</span> 수준입니다.",
            unsafe_allow_html=True,
        )

        # Plotly 차트 출력
        fig = go.Figure(
            go.Bar(
                x=["삼성전자", "SK하이닉스"],
                y=[samsung_cap, hynix_cap],
                # 사이트바 고유 컬러 반영: 네온 블루, 네온 오렌지
                marker_color=["#00ffff", "#ff9900"],
                text=[f"{samsung_cap:,.1f}조", f"{hynix_cap:,.1f}조"],
                textposition="auto",
            )
        )
        fig.update_layout(
            title={
                "text": "실시간 시가총액 비교 (단위: 조 원)",
                "font": {"color": "#e0e0e0"},
            },
            xaxis={"title": "기업명", "tickfont": {"color": "#aaa"}},
            yaxis={"title": "시가총액", "tickfont": {"color": "#aaa"}},
            template="plotly_dark", # 어두운 테마 그래프로 변경
            height=400,
            # 네온 그림자 효과 적용
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(
            f"<span class='neon-orange'>데이터 네트워크 치명적 오류 발생: {e}</span>",
            unsafe_allow_html=True,
        )


# 앱 실행
render_dashboard()
