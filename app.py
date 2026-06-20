import streamlit as st
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="코스피 4대장 시총 대시보드", page_icon="🔥", layout="wide")

# 전체 페이지 기본 스타일
modern_css = """
<style>
    .stApp { background-color: #f5f7fa; font-family: 'Pretendard', sans-serif; }
    
    .main-title { 
        font-size: 2.8rem; font-weight: 900; text-align: center; margin-bottom: 5px; 
        background: linear-gradient(45deg, #FF3CAC, #784BA0, #2B86C5, #FF3CAC);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-text 4s ease infinite;
        letter-spacing: -1px; line-height: 1.2;
    }
    @keyframes gradient-text {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .sub-title { text-align: center; color: #86868b; font-size: 1.05rem; margin-bottom: 30px; font-weight: 500; }
</style>
"""
st.markdown(modern_css, unsafe_allow_html=True)

st.markdown("<div class='main-title'>코스피 4대장<br>현재가 및 시총</div>", unsafe_allow_html=True)

# 메모리(세션 상태)에 가격 데이터를 저장할 공간 만들기
if 'prices' not in st.session_state:
    st.session_state.prices = {}

# 네이버 크롤링 함수
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
        if res.status_code != 200: return 0
        soup = BeautifulSoup(res.text, 'html.parser')
        today_div = soup.find('div', {'class': 'today'})
        if today_div:
            return int(today_div.find('span', {'class': 'blind'}).text.replace(',', ''))
        return 0
    except Exception:
        return 0

# 10초 갱신 프래그먼트
@st.fragment(run_every=10)
def render_dashboard():
    # 1. 현재 한국 시간(KST) 확인
    kst = timezone(timedelta(hours=9))
    now = datetime.now(kst)
    is_weekend = now.weekday() >= 5 # 5: 토요일, 6: 일요일
    is_active_hours = (8 <= now.hour < 20) # 08:00 ~ 19:59 사이 여부
    
    # 지금이 장 운영 시간인지 판별
    is_market_open = is_active_hours and not is_weekend

    if is_market_open:
        st.markdown(f"<div class='sub-title'>⚡ 실시간 연동 중 (최근 갱신: {now.strftime('%H:%M:%S')})</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='sub-title'>🌙 장 마감 시간입니다. (평일 08:00~20:00 외 네이버 갱신 중지)</div>", unsafe_allow_html=True)

    st.markdown("---")

    stocks = {
        "삼성전자": {"code": "005930", "shares": 5969782550, "color": "#0A47A3"},
        "SK하이닉스": {"code": "000660", "shares": 728002365, "color": "#E63312"},
        "SK스퀘어": {"code": "402340", "shares": 137348730, "color": "#F29023"},
        "삼성전기": {"code": "009150", "shares": 74693696, "color": "#1428A0"}
    }

    # 2. 크롤링 수행 여부 결정
    # 장이 열려있거나, 혹은 앱을 처음 켜서 저장된 가격이 하나도 없을 때만 데이터를 가져옵니다.
    needs_fetch = is_market_open or len(st.session_state.prices) == 0

    if needs_fetch:
        for name, info in stocks.items():
            price = get_realtime_price_naver(info["code"])
            if price != 0:
                st.session_state.prices[name] = price # 세션에 최신 가격 저장

    # 만약 네이버에서 한 번도 데이터를 못 가져왔다면 에러 처리
    if len(st.session_state.prices) == 0:
        st.warning("데이터를 불러오지 못했습니다. 잠시 후 다시 시도됩니다.")
        return

    # 3. 저장된 세션 가격을 이용해 시총 계산
    caps = {}
    for name, info in stocks.items():
        current_price = st.session_state.prices[name]
        caps[name] = (current_price * info["shares"]) / 1000000000000

    samsung_cap = caps["삼성전자"]
    hynix_cap = caps["SK하이닉스"]
    diff_cap = samsung_cap - hynix_cap
    percentage = (hynix_cap / samsung_cap) * 100

    # ==========================================
    # 📸 커스텀 '게섯거라' UI 생성 부분
    # ==========================================
    chaser_html = f"""
    <style>
        .chaser-card {{
            background: #ffffff;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            margin-bottom: 40px;
            border: 1px solid #f0f0f0;
        }}
        .chaser-header {{
            color: #d94833;
            font-size: 1.4rem;
            font-weight: 800;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .chaser-body {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: 25px;
        }}
        .c-col {{ display: flex; flex-direction: column; }}
        .c-right {{ text-align: right; }}
        
        .c-name {{ font-size: 1.3rem; font-weight: 800; color: #222; margin-bottom: 5px; }}
        .c-val {{ font-size: 1.1rem; color: #888; font-weight: 500; }}
        .c-diff {{ 
            font-size: 1.8rem; font-weight: 800; color: #d94833; 
            text-align: center; flex-grow: 1; margin: 0 20px;
        }}
        
        .prog-bg {{
            background-color: #f1f1f1;
            border-radius: 30px;
            height: 32px;
            width: 100%;
            position: relative;
        }}
        .prog-fill {{
            background-color: #d94833;
            border-radius: 30px;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 15px;
            color: white;
            font-weight: 800;
            font-size: 1.1rem;
            transition: width 0.5s ease;
            box-shadow: 2px 0 10px rgba(217, 72, 51, 0.4);
        }}
    </style>

    <div class="chaser-card">
        <div class="chaser-header">🏃‍♂️ 게섯거라 삼성전자!</div>
        <div class="chaser-body">
            <div class="c-col">
                <span class="c-name">SK하이닉스</span>
                <span class="c-val">{hynix_cap:,.1f}조 원</span>
            </div>
            <div class="c-diff">{diff_cap:,.1f}조 원 차이</div>
            <div class="c-col c-right">
                <span class="c-name">삼성전자</span>
                <span class="c-val">{samsung_cap:,.1f}조 원</span>
            </div>
        </div>
        <div class="prog-bg">
            <div class="prog-fill" style="width: {percentage}%;">
                {percentage:.1f}%
            </div>
        </div>
    </div>
    """
    
    st.markdown(chaser_html, unsafe_allow_html=True)

    # 하단 바 차트
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
        height=400,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

render_dashboard()
