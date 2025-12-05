import streamlit as st
import requests
import yfinance as yf

# ===================== PREMIUM CSS =====================

st.markdown("""
<style>

.premium-card {
    padding:22px;
    border-radius:20px;
    background:rgba(255,255,255,0.06);
    border:1px solid rgba(255,255,255,0.18);
    backdrop-filter: blur(14px);
    box-shadow:0 6px 24px rgba(0,0,0,0.35);
    text-align:center;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.premium-card:hover {
    transform: translateY(-4px) scale(1.03);
    box-shadow: 0 10px 32px rgba(0,0,0,0.50);
}

.premium-title {
    font-size:16px;
    color:#E5ECF5;
    font-weight:600;
    margin-bottom:6px;
}

.premium-value {
    font-size:38px;
    font-weight:800;
    color:white;
    margin-top:-4px;
}

.premium-sub {
    font-size:14px;
    color:#AAB4C2;
    margin-top:8px;
}

/* Glow Badge */
.glow-badge {
    padding:4px 12px;
    border-radius:10px;
    color:white;
    font-size:12px;
    font-weight:600;
    box-shadow:0 0 8px rgba(255,255,255,0.4);
}

/* Animated Sentiment Bar */
.sentibar-container {
    width:100%;
    height:22px;
    border-radius:12px;
    background:#1a1a1a;
    overflow:hidden;
    border:1px solid rgba(255,255,255,0.15);
    margin-top:15px;
}

.sentibar-fill {
    height:100%;
    background:linear-gradient(90deg,#16e06f,#f1c40f,#e74c3c);
    background-size:300% 100%;
    animation:flow 4s linear infinite;
}

@keyframes flow {
    0% {background-position:0%;}
    100% {background-position:200%;}
}

</style>
""", unsafe_allow_html=True)


# ===================== API FUNCTIONS =====================

def get_fear_greed():
    try:
        url = "https://api.alternative.me/fng/?limit=1&format=json"
        data = requests.get(url, timeout=5).json()
        value = int(data["data"][0]["value"])
        rating = data["data"][0]["value_classification"]
        return value, rating
    except:
        return None, None


def get_btc_dominance():
    try:
        url = "https://api.coingecko.com/api/v3/global"
        data = requests.get(url, timeout=5).json()
        dom = data["data"]["market_cap_percentage"]["btc"]
        return round(float(dom), 2)
    except:
        return None


def get_btc_momentum():
    df = yf.download("BTC-USD", period="10d", interval="1d")
    if df.empty or len(df) < 7:
        return None
    close = df["Close"]
    try:
        change = (close.iloc[-1] - close.iloc[-7]) / close.iloc[-7] * 100
        return round(float(change), 2)
    except:
        return None


def get_volume_pulse():
    df = yf.download("BTC-USD", period="15d", interval="1d")
    if df.empty:
        return None
    vol = df["Volume"]
    try:
        pulse = (vol.iloc[-1] - vol.mean()) / vol.mean() * 100
        return round(float(pulse), 2)
    except:
        return None


# ===================== UI COMPONENTS =====================

def badge(text, color):
    return f'<span class="glow-badge" style="background-color:{color};">{text}</span>'


def premium_card(title, value, subtext="", icon="💠"):
    return f"""
    <div class="premium-card">
        <div class="premium-title">{icon} {title}</div>
        <div class="premium-value">{value}</div>
        <div class="premium-sub">{subtext}</div>
    </div>
    """


# ===================== RENDER PREMIUM SENTIMENT =====================

def render_crypto_sentiment():

    st.markdown("## 🧭 Crypto Market Sentiment (Premium)")

    fear, fear_label = get_fear_greed()
    btc_dom = get_btc_dominance()
    mom = get_btc_momentum()
    pulse = get_volume_pulse()

    mom = float(mom) if mom is not None else None
    pulse = float(pulse) if pulse is not None else None

    if fear is None: mood_icon = "⚪️"
    elif fear > 55: mood_icon = "🟢"
    elif fear > 25: mood_icon = "🟡"
    else: mood_icon = "🔴"

    mom_icon = "↗" if mom and mom > 0 else "↘"
    pulse_icon = "↗" if pulse and pulse > 0 else "↘"

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        val = f"{fear}/100" if fear is not None else "N/A"
        if fear is not None and fear_label:
            col = "#2ecc71" if fear > 55 else "#f1c40f" if fear > 25 else "#e74c3c"
            sub = badge(fear_label, col)
        else:
            sub = ""
        st.markdown(premium_card("Fear & Greed Index", val, sub, icon=mood_icon), unsafe_allow_html=True)

    with c2:
        val = f"{btc_dom:.2f}%" if btc_dom is not None else "N/A"
        st.markdown(premium_card("BTC Dominance", val, "Market Strength Indicator", icon="🧲"), unsafe_allow_html=True)

    with c3:
        val = f"{mom:.2f}%" if mom is not None else "N/A"
        col = "#2ecc71" if mom and mom > 0 else "#e74c3c"
        sub = badge("Bullish" if mom and mom > 0 else "Bearish", col)
        st.markdown(premium_card("BTC Momentum (7d)", val, sub, icon=mom_icon), unsafe_allow_html=True)

    with c4:
        val = f"{pulse:.2f}%" if pulse is not None else "N/A"
        col = "#2ecc71" if pulse and pulse > 0 else "#e74c3c"
        sub = badge("High Liquidity" if pulse and pulse > 0 else "Low Liquidity", col)
        st.markdown(premium_card("Volume Pulse", val, sub, icon=pulse_icon), unsafe_allow_html=True)

    score = fear if fear is not None else 50

    st.markdown(f"""
        <div class="sentibar-container">
            <div class="sentibar-fill" style="width:{score}%"></div>
        </div>
    """, unsafe_allow_html=True)
