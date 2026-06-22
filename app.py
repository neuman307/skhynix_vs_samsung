import streamlit as st
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="코스피 4대장 시총 대시보드", page_icon="🔥", layout="wide")

# 기존 CSS에 하이퍼리퀴드 전용 다크 테마 CSS 추가
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

    /* 게섯거라 UI */
    .pg-container {
        background: #ffffff; border-radius: 16px; padding: 25px 30px 35px 30px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04); border: 1px solid #eaeaea;
        margin-bottom: 30px;
    }
    .pg-title { font-size: 1.1rem; font-weight: 800; color: #E63312; margin-bottom: 20px; }
    .pg-labels { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
    .pg-label-box { display: flex; flex-direction: column; }
    .pg-label-name { font-size: 1.05rem; font-weight: 800; color: #333; white-space: nowrap; }
    .pg-label-cap { font-size: 0.9rem; font-weight: 600; color: #86868b; margin-top: 3px; white-space: nowrap; }
    .pg-diff { color: #E63312; font-weight: 900; font-size: 1.7rem; letter-spacing: -0.5px; white-space: nowrap; text-align: center; margin: 0 10px; }
    .pg-track { background-color: #e9ecef; height: 14px; border-radius: 10px; position: relative; width: 100%; }
    .pg-fill { background-color: #E63312; height: 100%; border-radius: 10px; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1); }
    .pg-thumb {
        position: absolute; top: 50%; transform: translate(-50%, -50%);
        background-color: #E63312; color: #ffffff; font-weight: 800; font-size: 0.85rem;
        padding: 4px 12px; border-radius: 20px; box-shadow: 0 2px 8px rgba(230, 51, 18, 0.4);
        transition: left 1s cubic-bezier(0.4, 0, 0.2, 1); white-space: nowrap;
    }

    /* 🌐 하이퍼리퀴드 전용 다크 테마 CSS */
    .hl-container {
        background: #18181b; border-radius: 16px; padding: 25px 30px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15); 
        margin-top: 40px; margin-bottom: 20px; border: 1px solid #27272a;
    }
    .hl-title { font-size: 1.15rem; font-weight: 800; color: #22d3ee; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;}
    .hl-rate { font-size: 0.9rem; font-weight: 600; color: #a1a1aa; }
    .hl-card-container { display: flex; gap: 15px; }
    .hl-card {
        background: #27272a; border: 1px solid #3f3f46;
        border-radius: 12px; padding: 20px; flex: 1;
        transition: transform 0.2s; text-align: center;
    }
    .hl-card:hover { transform: translateY(-3px); border-color: #22d3ee; }
    .hl-name { font-size: 1.05rem; font-weight: 700; color: #e4e4e7; margin-bottom: 10px; }
    .hl-krw { font-size: 1.6rem; font-weight: 900; color: #ffffff; margin-bottom: 5px; }
    .hl-usd { font-size: 0.95rem; font-weight: 500; color: #a1a1aa; }

    @media (max-width: 600px) {
        .pg-container { padding: 20px 15px 35px 15px; }
        .pg-title { font-size: 1rem; margin-bottom: 15px; }
        .pg-diff { font-size: 1.15rem; margin: 0 5px; }
        .pg-label-name { font-size: 0.85rem; }
        .pg-label-cap { font-size: 0.75rem; }
        .main-title { font-size: 2.2rem; }
        .hl-card-container { flex-direction: column; }
        .hl-title { flex-direction: column; align-items: flex-start; gap: 8px; }
    }
</style>
"""
st.markdown(modern_css, unsafe_allow_html=True)

st.markdown("<div class='main-title'>코스피 4대장<br>현재가 및 시총</div>", unsafe_allow_html=True)

# 초기 상태 세팅 (가격 및 환율)
if 'prices' not in st.session_state:
    st.session_state.prices = {}
if 'exchange_rate' not in st.session_state:
    st.session_state.exchange_rate = 1380.0

# 1. 네이버 금융 (국내 주가) 크롤링 함수
def get_realtime_price_naver(code):
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15'}
    try:
        res = requests.get(url, headers=headers, timeout=3)
        if res.status_code != 200: return 0
        soup = BeautifulSoup(res.text, 'html.parser')
        today_div = soup.find('div', {'class': 'today'})
        if today_div: return int(today_div.find('span', {'class': 'blind'}).text.replace(',', ''))
        return 0
    except Exception:
        return 0

# 2. 네이버 금융 (환율) 크롤링 함수
def get_usd_krw_rate():
    url = "https://finance.naver.com/marketindex/"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15'}
    try:
        res = requests.get(url, headers=headers, timeout=3)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            rate_str = soup.select_one('#exchangeList > li.on > a.head.usd > div > span.value').text
            return float(rate_str.replace(',', ''))
    except Exception:
        pass
    return 0

# 3. 하이퍼리퀴드 공식 API 호출 함수 (가상자산/선물 단가)
def get_hyperliquid_prices(assets):
    url = "https://api.hyperliquid.xyz/info"
    payload = {"type": "metaAndAssetCtxs"}
    try:
        res = requests.post(url, json=payload, timeout=3).json()
        universe = res[0]['universe']
        ctxs = res[1]
        
        prices = {}
        for i, asset in enumerate(universe):
            if asset['name'] in assets:
                prices[asset['name']] = float(ctxs[i]['markPx'])
        return prices
    except Exception:
        return {}


@st.fragment(run_every=10)
def render_dashboard():
    try:
        # 시간 검증 (KST 기준 평일 08시 ~ 20시)
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst)
        is_weekend = now.weekday() >= 5
        is_active_hours = (8 <= now.hour < 20)
        is_market_open = is_active_hours and not is_weekend

        if is_market_open:
            st.markdown(f"<div class='sub-title'>⚡ 실시간 연동 중 (최근 갱신: {now.strftime('%H:%M:%S')})</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='sub-title'>🌙 장 마감 시간입니다. (국내 주가 네이버 크롤링 중지)</div>", unsafe_allow_html=True)

        stocks = {
            "삼성전자": {"code": "005930", "shares": 5846279000, "color": "#0A47A3"},
            "SK하이닉스": {"code": "000660", "shares": 712702365, "color": "#E63312"},
            "SK스퀘어": {"code": "402340", "shares": 131958000, "color": "#F29023"},
            "삼성전기": {"code": "009150", "shares": 74693696, "color": "#1428A0"}
        }

        # KOSPI & 환율 크롤링 실행 (장이 열려있거나 최초 실행일 때만 동작)
        needs_kospi_fetch = is_market_open or len(st.session_state.prices) == 0

        if needs_kospi_fetch:
            for name, info in stocks.items():
                price = get_realtime_price_naver(info["code"])
                if price != 0:
                    st.session_state.prices[name] = price
            
            # 환율도 장이 열려있을 때만 가져와서 네이버 차단 방지
            current_rate = get_usd_krw_rate()
            if current_rate != 0:
                st.session_state.exchange_rate = current_rate
        
        if len(st.session_state.prices) == 0:
            st.warning("데이터를 불러오지 못했습니다. 잠시 후 다시 시도됩니다.")
            return

        # 시총 계산
        caps = {}
        prices = {}
        for name, info in stocks.items():
            prices[name] = st.session_state.prices[name]
            caps[name] = (prices[name] * info["shares"]) / 1000000000000

        samsung_cap = caps["삼성전자"]
        hynix_cap = caps["SK하이닉스"]
        hynix_ratio = (hynix_cap / samsung_cap) * 100
        bar_width = min(hynix_ratio, 100)
        diff_cap = samsung_cap - hynix_cap 
        
        # 게섯거라 UI 렌더링
        progress_html = f"""
        <div class="pg-container">
            <div class="pg-title">🏃‍♂️ 게섯거라 삼성전자!</div>
            <div class="pg-labels">
                <div class="pg-label-box" style="text-align: left;">
                    <span class="pg-label-name">SK하이닉스</span>
                    <span class="pg-label-cap">{hynix_cap:,.1f}조 원</span>
                </div>
                <div class="pg-diff">{diff_cap:,.1f}조 원 차이</div>
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

        # 4대장 카드 렌더링
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

                st.metric(label=f"{name}", value=f"{prices[name]:,} 원", delta=delta_text, delta_color=delta_color)

        st.markdown("<br>", unsafe_allow_html=True)

        # 차트 렌더링
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
            template="plotly_white", height=450, margin=dict(l=40, r=40, t=60, b=40),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

        # =====================================================================
        # [NEW] 하이퍼리퀴드 24H 실시간 시세 연동 (주말/야간 무관하게 무조건 갱신)
        # =====================================================================
        hl_prices = get_hyperliquid_prices(["SMSN", "SKHX"])
        hl_samsung_usd = hl_prices.get("SMSN", 0.0)
        hl_hynix_usd = hl_prices.get("SKHX", 0.0)
        
        # 하이퍼리퀴드에서 데이터를 정상적으로 받아왔을 때만 하단에 위젯 표시
        if hl_samsung_usd > 0 or hl_hynix_usd > 0:
            hl_samsung_krw = hl_samsung_usd * st.session_state.exchange_rate
            hl_hynix_krw = hl_hynix_usd * st.session_state.exchange_rate

            hl_html = f"""
            <div class="hl-container">
                <div class="hl-title">
                    <span>🌐 글로벌 24H 파생 시세 (Hyperliquid)</span>
                    <span class="hl-rate">적용 환율: ₩{st.session_state.exchange_rate:,.1f} / $</span>
                </div>
                <p style="color: #a1a1aa; font-size: 0.9rem; margin-top: -5px; margin-bottom: 20px; line-height: 1.4;">
                    국내 코스피 장이 마감된 야간이나 주말에도 <strong>24시간 쉬지 않고 거래</strong>되는 하이퍼리퀴드의 삼성전자(SMSN)와 SK하이닉스(SKHX) 선물 단가입니다.
                </p>
                <div class="hl-card-container">
                    <div class="hl-card">
                        <div class="hl-name">SK하이닉스 (SKHX)</div>
                        <div class="hl-krw">₩ {hl_hynix_krw:,.0f}</div>
                        <div class="hl-usd">$ {hl_hynix_usd:,.2f}</div>
                    </div>
                    <div class="hl-card">
                        <div class="hl-name">삼성전자 (SMSN)</div>
                        <div class="hl-krw">₩ {hl_samsung_krw:,.0f}</div>
                        <div class="hl-usd">$ {hl_samsung_usd:,.2f}</div>
                    </div>
                </div>
            </div>
            """
            st.markdown(hl_html, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")

render_dashboard()
