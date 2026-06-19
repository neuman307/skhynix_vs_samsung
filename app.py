import streamlit as st
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

st.set_page_config(page_title="국내 주요 Tech 시총 비교", page_icon="📈", layout="wide")

# (기존에 사용했던 modern_css 스타일 코드는 그대로 유지합니다)
modern_css = """
<style>
    .stApp { background-color: #f5f7fa; font-family: 'Pretendard', sans-serif; }
    .main-title { font-size: 2.2rem; font-weight: 800; color: #1d1d1f; text-align: center; margin-bottom: 5px; }
    .sub-title { text-align: center; color: #86868b; font-size: 1.05rem; margin-bottom: 30px; }
    div[data-testid="metric-container"] {
        background-color: #ffffff; border-radius: 16px; padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04); border: 1px solid #eaeaea;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="metric-container"]:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08); }
    div[data-testid="stMetricLabel"] { color: #515154 !important; font-weight: 600 !important; font-size: 1.1rem !important; }
    div[data-testid="stMetricValue"] { color: #1d1d1f !important; font-weight: 800 !important; font-size: 1.9rem !important; }
</style>
"""
st.markdown(modern_css, unsafe_allow_html=True)

st.markdown("<div class='main-title'>국내 주요 Tech 기업 시가총액 비교</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>⚡ 네이버 금융 실시간 연동 (10초 자동 갱신)</div>", unsafe_allow_html=True)
st.markdown("---")

# 네이버 금융에서 실시간 현재가를 크롤링하는 함수
# 네이버 금융에서 실시간 현재가를 크롤링하는 함수 (강화 버전)
def get_realtime_price_naver(code):
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    
    # 일반 사람의 브라우저인 것처럼 완벽하게 위장하는 헤더
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Referer': 'https://finance.naver.com/'
    }
    
    try:
        # 타임아웃을 3초로 주어 무한정 멈춰있는 것 방지
        res = requests.get(url, headers=headers, timeout=3)
        
        # 200(정상)이 아니면 차단당한 것
        if res.status_code != 200:
            st.error(f"[{code}] 네이버 접속 차단됨 (에러 코드: {res.status_code})")
            return 0
            
        soup = BeautifulSoup(res.text, 'html.parser')
        
        today_div = soup.find('div', {'class': 'today'})
        if today_div:
            price_str = today_div.find('span', {'class': 'blind'}).text
            return int(price_str.replace(',', ''))
        else:
            st.error(f"[{code}] 페이지 구조를 읽지 못했습니다. (봇 방지 캡차 의심)")
            return 0
            
    except requests.exceptions.Timeout:
        st.error(f"[{code}] 네이버 응답이 너무 느립니다. (타임아웃)")
        return 0
    except Exception as e:
        st.error(f"[{code}] 오류 발생: {e}")
        return 0


# 10초마다 재실행 (차단 방지를 위해 시간 상향)
@st.fragment(run_every=10)
def render_dashboard():
    try:
        stocks = {
            "삼성전자": {"code": "005930", "shares": 5969782550, "color": "#0A47A3"},
            "SK하이닉스": {"code": "000660", "shares": 728002365, "color": "#E63312"},
            "SK스퀘어": {"code": "402340", "shares": 137348730, "color": "#F29023"},
            "삼성전기": {"code": "009150", "shares": 74693696, "color": "#1428A0"}
        }

        caps = {}
        prices = {}

        # 네이버 실시간 데이터 크롤링
        for name, info in stocks.items():
            price = get_realtime_price_naver(info["code"])
            if price == 0:
                st.warning(f"{name} 실시간 데이터를 불러오지 못했습니다.")
                return
            
            prices[name] = price
            caps[name] = (price * info["shares"]) / 1000000000000

        samsung_cap = caps["삼성전자"]

        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        columns = [col1, col2, col3, col4]

        for i, (name, info) in enumerate(stocks.items()):
            with columns[i]:
                current_cap = caps[name]
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

        fig = go.Figure(
            go.Bar(
                x=list(stocks.keys()),
                y=list(caps.values()),
                marker_color=[info["color"] for info in stocks.values()],
                text=[f"{cap:,.1f}조" for cap in caps.values()],
                textposition="auto",
                textfont=dict(color='white', size=14, weight='bold')
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
        st.error(f"네트워크 오류가 발생했습니다: {e}")

render_dashboard()
