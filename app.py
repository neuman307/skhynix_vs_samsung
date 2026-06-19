import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. 페이지 테마 설정 (넓은 화면 사용)
st.set_page_config(page_title="국내 주요 Tech 시총 비교", page_icon="📈", layout="wide")

# 2. 세련된 모던(Light) 스타일 CSS 주입
modern_css = """
<style>
    /* 전체 배경: 부드러운 라이트 그레이 */
    .stApp {
        background-color: #f5f7fa;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* 깔끔한 한 줄 제목 스타일 */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1d1d1f; /* 짙은 다크 그레이 */
        text-align: center;
        margin-bottom: 5px;
        letter-spacing: -0.5px;
    }
    .sub-title {
        text-align: center;
        color: #86868b;
        font-size: 1.05rem;
        margin-bottom: 30px;
    }

    /* 애플/토스 스타일의 글래스모피즘 카드 */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        border: 1px solid #eaeaea;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    }
    
    /* 메트릭 텍스트 가독성 극대화 */
    div[data-testid="stMetricLabel"] {
        color: #515154 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    div[data-testid="stMetricValue"] {
        color: #1d1d1f !important;
        font-weight: 800 !important;
        font-size: 1.9rem !important;
    }
</style>
"""

st.markdown(modern_css, unsafe_allow_html=True)

# 제목 표시
st.markdown("<div class='main-title'>국내 주요 Tech 기업 시가총액 비교</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>실시간 주가 연동 대시보드 (5초 자동 갱신)</div>", unsafe_allow_html=True)
st.markdown("---")

# 5초마다 이 안의 코드만 재실행
@st.fragment(run_every=5)
def render_dashboard():
    try:
        # 4개 종목의 티커(Ticker), 대략적 발행주식수, 브랜드 컬러 설정
        stocks = {
            "삼성전자": {"ticker": "005930.KS", "shares": 5969782550, "color": "#0A47A3"},
            "SK하이닉스": {"ticker": "000660.KS", "shares": 728002365, "color": "#E63312"},
            "SK스퀘어": {"ticker": "402340.KS", "shares": 137348730, "color": "#F29023"},
            "삼성전기": {"ticker": "009150.KS", "shares": 74693696, "color": "#1428A0"}
        }

        caps = {}
        prices = {}

        # 3. 데이터 수집 및 계산 (각 종목별 최신가 가져오기)
        for name, info in stocks.items():
            data = yf.Ticker(info["ticker"]).history(period="1d")
            if data.empty:
                st.warning(f"{name} 데이터를 불러올 수 없습니다.")
                return
            
            # 현재가 및 시총(조 단위) 계산
            prices[name] = int(data["Close"].iloc[-1])
            caps[name] = (prices[name] * info["shares"]) / 1000000000000

        # 기준이 되는 삼성전자 시총
        samsung_cap = caps["삼성전자"]

        # 4. 카드형 UI 배치 (2x2 그리드 배열)
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        columns = [col1, col2, col3, col4]

        for i, (name, info) in enumerate(stocks.items()):
            with columns[i]:
                current_cap = caps[name]
                
                # 삼성전자는 시총 수치를 보여주고, 나머지는 삼성 대비 %를 보여줌
                if name == "삼성전자":
                    delta_text = f"{current_cap:,.1f} 조 원"
                    delta_color = "off"
                else:
                    percentage = (current_cap / samsung_cap) * 100
                    delta_text = f"삼성 대비 {percentage:.2f}%"
                    delta_color = "normal"

                st.metric(
                    label=f"{name}",
                    value=f"{prices[name]:,} 원",
                    delta=delta_text,
                    delta_color=delta_color
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # 5. 깔끔한 막대 그래프 출력
        fig = go.Figure(
            go.Bar(
                x=list(stocks.keys()),
                y=list(caps.values()),
                marker_color=[info["color"] for info in stocks.values()],
                text=[f"{cap:,.1f}조" for cap in caps.values()],
                textposition="auto",
                textfont=dict(color='white', size=14, weight='bold') # 막대 안의 글씨는 하얗게
            )
        )
        
        fig.update_layout(
            title=dict(text="기업별 시가총액 비교 차트", font=dict(size=18, color="#1d1d1f")),
            xaxis=dict(tickfont=dict(size=14, color="#515154")),
            yaxis=dict(title="시가총액 (조 원)", tickfont=dict(color="#515154")),
            template="plotly_white",
            height=450,
            margin=dict(l=40, r=40, t=60, b=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"데이터 갱신 중 오류가 발생했습니다: {e}")

# 앱 실행
render_dashboard()
