import streamlit as st
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

st.set_page_config(page_title="코스피 4대장 시총 대시보드", page_icon="🔥", layout="wide")

# 화려한 타이틀과 모던 카드 스타일 CSS 적용
modern_css = """
<style>
    .stApp { background-color: #f5f7fa; font-family: 'Pretendard', sans-serif; }
    
    /* 화려한 애니메이션 그라데이션 타이틀 */
    .main-title { 
        font-size: 2.8rem; 
        font-weight: 900; 
        text-align: center; 
        margin-bottom: 5px; 
        /* 트렌디한 그라데이션 색상 조합 */
        background: linear-gradient(45deg, #FF3CAC, #784BA0, #2B86C5, #FF3CAC);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-text 4s ease infinite;
        text-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        letter-spacing: -1px;
    }
    
    /* 타이틀 애니메이션 키프레임 */
    @keyframes gradient-text {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .sub-title { text-align: center; color: #86868b; font-size: 1.05rem; margin-bottom: 30px; font-weight: 500; }
    
    /* 깔끔한 글래스모피즘 카드 */
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

# 변경된 화려한 제목
st.markdown("<div class='main-title'>코스피 4대장 현재가 및 시총</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>⚡ 네이버 금융 실시간 연동 (10초 자동 갱신)</div>", unsafe_allow_html=True)
st.markdown("---")

# 네이버 금융 크롤링 함수
def get_realtime_price_naver(code):
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Referer': 'https://finance.naver.com/'
    }
    try:
        res = requests.get(url, headers=headers, timeout=3)
        if res.status_code != 200:
            st.error(f"[{code}] 접속 차단 (에러 코드: {res.status_code})")
            return 0
        soup = BeautifulSoup(res.text, 'html.parser')
        today_div = soup.find('div', {'class': 'today'})
        if today_div:
            price_str = today_div.find('span', {'class': 'blind'}).text
            return int(price_str.replace(',', ''))
        return 0
    except Exception as e:
        st.error(f"[{code}] 오류 발생: {e}")
        return 0

# 10초마다 데이터 갱신
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
                
                # 1. 삼성전자는 시총 수치 표기
                if name == "삼성전자":
                    delta_text = f"{current_cap:,.1f} 조 원"
                    delta_color = "off"
                
                # 2. SK하이닉스는 퍼센트 + 차이나는 시총(조 원) 함께 표기
                elif name == "SK하이닉스":
                    percentage = (current_cap / samsung_cap) * 100
                    diff_cap = samsung_cap - current_cap # 차이나는 금액 계산
                    delta_text = f"삼성 대비 {percentage:.2f}% ( -{diff_cap:,.1f}조 차이 )"
                    delta_color = "normal"
                
                # 3. 나머지는 퍼센트만 표기
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
            title=dict(text="실시간 시가총액 비교 차트", font=dict(size=18, color="#1d1d1f")),
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
