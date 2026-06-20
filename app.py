import streamlit as st
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="코스피 4대장 시총 대시보드", page_icon="🔥", layout="wide")

# 모바일 반응형 및 줄바꿈 방지가 추가된 CSS
modern_css = """
<style>
    .stApp { background-color: #f5f7fa; font-family: 'Pretendard', sans-serif; }
    
    .main-title { 
        font-size: 2.8rem; 
        font-weight: 900; 
        text-align: center; 
        margin-bottom: 5px; 
        background: linear-gradient(45deg, #FF3CAC, #784BA0, #2B86C5, #FF3CAC);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-text 4s ease infinite;
        text-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        letter-spacing: -1px;
        line-height: 1.2;
    }
    
    @keyframes gradient-text {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .sub-title { text-align: center; color: #86868b; font-size: 1.05rem; margin-bottom: 20px; font-weight: 500; }
    
    div[data-testid="metric-container"] {
        background-color: #ffffff; border-radius: 16px; padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04); border: 1px solid #eaeaea;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="metric-container"]:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08); }
    div[data-testid="stMetricLabel"] { color: #515154 !important; font-weight: 600 !important; font-size: 1.1rem !important; }
    div[data-testid="stMetricValue"] { color: #1d1d1f !important; font-weight: 800 !important; font-size: 1.9rem !important; }

    .pg-container {
        background: #ffffff; border-radius: 16px; padding: 25px 30px 35px 30px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04); border: 1px solid #eaeaea;
        margin-bottom: 30px;
    }
    .pg-title { font-size: 1.1rem; font-weight: 800; color: #E63312; margin-bottom: 20px; }
    
    .pg-labels {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 15px;
    }
    .pg-label-box { display: flex; flex-direction: column; }
    /* 💡 줄바꿈(nowrap) 방지 추가 */
    .pg-label-name { font-size: 1.05rem; font-weight: 800; color: #333; white-space: nowrap; }
    .pg-label-cap { font-size: 0.9rem; font-weight: 600; color: #86868b; margin-top: 3px; white-space: nowrap; }
    .pg-diff { color: #E63312; font-weight: 900; font-size: 1.7rem; letter-spacing: -0.5px; white-space: nowrap; text-align: center; margin: 0 10px; }

    .pg-track { background-color: #e9ecef; height: 14px; border-radius: 10px; position: relative; width: 100%; }
    .pg-fill {
        background-color: #E63312; height: 100%; border-radius: 10px;
        transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .pg-thumb {
        position: absolute; top: 50%; transform: translate(-50%, -50%);
        background-color: #E63312; color: #ffffff; font-weight: 800; font-size: 0.85rem;
        padding: 4px 12px; border-radius: 20px; box-shadow: 0 2px 8px rgba(230, 51, 18, 0.4);
        transition: left 1s cubic-bezier(0.4, 0, 0.2, 1);
        white-space: nowrap;
    }

    /* 📱 모바일 화면(가로 600px 이하) 전용 스타일 */
    @media (max-width: 600px) {
        .pg-container { padding: 20px 15px 35px 15px; } /* 좌우 여백 축소 */
        .pg-title { font-size: 1rem; margin-bottom: 15px; }
        .pg-diff { font-size: 1.15rem; margin: 0 5px; } /* 중앙 차이 금액 폰트 대폭 축소 */
        .pg-label-name { font-size: 0.85rem; } /* 종목명 축소 */
        .pg-label-cap { font-size: 0.75rem; } /* 시총 수치 축소 */
        .main-title { font-size: 2.2rem; } /* 메인 타이틀 크기도 모바일에 맞게 축소 */
    }
</style>
"""
st.markdown(modern_css, unsafe_allow_html=True)

st.markdown("<div class='main-title'>코스피 4대장<br>현재가 및 시총</div>", unsafe_allow_html=True)

# 메모리(세션 상태)에 가격 데이터를 저장할 공간
if 'prices' not in st.session_state:
    st.session_state.prices = {}

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

@st.fragment(run_every=10)
def render_dashboard():
    try:
        # 1. 한국 시간(KST) 및 장 운영 여부 확인
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst)
        is_weekend = now.weekday() >= 5 # 5: 토요일, 6: 일요일
        is_active_hours = (8 <= now.hour < 20) # 08:00 ~ 19:59 사이 여부
        
        is_market_open = is_active_hours and not is_weekend

        # 상태 안내 메시지 표기
        if is_market_open:
            st.markdown(f"<div class='sub-title'>⚡ 실시간 연동 중 (최근 갱신: {now.strftime('%H:%M:%S')})</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='sub-title'>🌙 장 마감 시간입니다. (평일 08:00~20:00 외 크롤링 중지)</div>", unsafe_allow_html=True)

        # 2. 업데이트된 발행 주식 수 적용
        stocks = {
            "삼성전자": {"code": "005930", "shares": 5919637922, "color": "#0A47A3"},
            "SK하이닉스": {"code": "000660", "shares": 712702365, "color": "#E63312"},
            "SK스퀘어": {"code": "402340", "shares": 137348730, "color": "#F29023"},
            "삼성전기": {"code": "009150", "shares": 74693696, "color": "#1428A0"}
        }

        # 3. 크롤링 실행 조건: 장이 열려있거나, 저장된 가격 데이터가 하나도 없을 때(최초 실행)
        needs_fetch = is_market_open or len(st.session_state.prices) == 0

        if needs_fetch:
            for name, info in stocks.items():
                price = get_realtime_price_naver(info["code"])
                if price != 0:
                    st.session_state.prices[name] = price # 정상적으로 받아왔을 때만 세션에 저장
        
        # 데이터가 없을 경우 에러 처리
        if len(st.session_state.prices) == 0:
            st.warning("데이터를 불러오지 못했습니다. 잠시 후 다시 시도됩니다.")
            return

        caps = {}
        prices = {}

        # 4. 세션에 저장된 가격(실시간 또는 마지막 종가)을 불러와 시총 계산
        for name, info in stocks.items():
            prices[name] = st.session_state.prices[name]
            caps[name] = (prices[name] * info["shares"]) / 1000000000000

        samsung_cap = caps["삼성전자"]
        hynix_cap = caps["SK하이닉스"]
        
        hynix_ratio = (hynix_cap / samsung_cap) * 100
        bar_width = min(hynix_ratio, 100)
        diff_cap = samsung_cap - hynix_cap 
        
        progress_html = f"""
<div class="pg-container">
    <div class="pg-title"> 🦀 게섯거라 삼성전자! 🏃‍♂️</div>
    <div class="pg-labels">
        <div class="pg-label-box" style="text-align: left;">
            <span class="pg-label-name">SK하이닉스</span>
            <span class="pg-label-cap">{hynix_cap:,.1f}조 원</span>
        </div>
        <div class="pg-diff">
            {diff_cap:,.1f}조 원 차이
        </div>
        <div class="pg-label-box" style="text-align: right;">
            <span class="pg-label-name">삼성전자</span>
            <span class="pg-label-cap">{samsung_cap:,.1f}조 원</span>
        </div>
    </div>
    <div class="pg-track">
        <div class="pg-fill" style="width: {bar_width}%;"></div>
        <div class="pg-thumb" style="left: {bar_width}%;">{hynix_ratio:.1f}%</div>
    </div>
</div>
"""
        st.markdown(progress_html, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        columns = [col1, col2, col3, col4]

        for i, (name, info) in enumerate(stocks.items()):
            with columns[i]:
                current_cap = caps[name]
                
                if name == "삼성전자":
                    delta_text = f"{current_cap:,.1f} 조 원"
                    delta_color = "off"
                elif name == "SK하이닉스":
                    delta_text = f"삼성 대비 {hynix_ratio:.2f}% ( -{diff_cap:,.1f}조 차이 )"
                    delta_color = "normal"
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
        st.error(f"오류가 발생했습니다: {e}")

render_dashboard()
