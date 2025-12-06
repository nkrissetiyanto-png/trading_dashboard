import streamlit as st
import requests
import yfinance as yf

# ===================== PREMIUM CSS =====================

st.markdown("""
<style>

.premium-card {
    width: 100%;
    margin-top: 12px;
    padding: 20px;
    border-radius: 18px;
    background: radial-gradient(circle at top left, rgba(59,130,246,0.18), transparent 55%),
                radial-gradient(circle at bottom right, rgba(239,68,68,0.18), transparent 55%),
                #020617;
    border: 1px solid rgba(148,163,184,0.45);
    box-shadow: 0 10px 30px rgba(15,23,42,0.9);
    text-align: center;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border 0.25s ease;
}

.premium-card:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 18px 40px rgba(15,23,42,1);
    border-color: rgba(248,250,252,0.6);
}

.premium-title {
    font-size: 15px;
    letter-spacing: 0.03em;
    color: #E5ECF5;
    font-weight: 600;
    margin-bottom: 6px;
}

.premium-value {
    font-size: 34px;
    font-weight: 800;
    color: #F9FAFB;
    margin-top: -2px;
}

.premium-sub {
    font-size: 13px;
    color: #CBD5F5;
    margin-top: 8px;
}

/* Glow Badge */
.glow-badge {
    padding: 4px 14px;
    border-radius: 999px;
    color: #F9FAFB;
    font-size: 12px;
    font-weight: 600;
    box-shadow: 0 0 14px rgba(248,250,252,0.45);
    display: inline-block;
}

/* Animated Sentiment Bar */
.sentibar-container {
    width: 100%;
    height: 22px;
    border-radius: 12px;
    background: #020617;
    overflow: hidden;
    border: 1px solid rgba(148,163,184,0.45);
    margin-top: 18px;
    box-shadow: 0 6px 20px rgba(15,23,42,0.85);
}

.sentibar-fill {
    height: 100%;
    background: linear-gradient(90deg,#16e06f,#f1c40f,#e74c3c);
    background-size: 300% 100%;
    animation: flow 4s linear infinite;
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


def get_price(symbol="BTC-USD"):
    try:
        df = yf.download(symbol, period="1d", interval="1m")
        if df.empty:
            return None, None

        current = float(df["Close"].iloc[-1])
        prev = float(df["Close"].iloc[-2])
        change = (current - prev) / prev * 100
        return round(current, 2), round(change, 2)

    except:
        return None, None

# ===================== UI COMPONENTS =====================

def badge(text, color):
    return f'<span class="glow-badge" style="background-color:{color};">{text}</span>'


def premium_card(title, value, subtext="", icon="💠"):
    # Single-line HTML supaya aman dirender Streamlit
    return (
        '<div class="premium-card">'
            f'<div class="premium-title">{icon} {title}</div>'
            f'<div class="premium-value">{value}</div>'
            f'<div class="premium-sub">{subtext}</div>'
        '</div>'
    )


# ===================== RENDER PREMIUM SENTIMENT =====================

def render_crypto_sentiment():
    st.markdown("## 🧭 Crypto Market Sentiment (Premium)")

    fear, fear_label = get_fear_greed()
    btc_dom = get_btc_dominance()
    mom = get_btc_momentum()
    pulse = get_volume_pulse()

    mom = float(mom) if mom is not None else None
    pulse = float(pulse) if pulse is not None else None

    if fear is None:
        mood_icon = "⚪️"
    elif fear > 55:
        mood_icon = "🟢"
    elif fear > 25:
        mood_icon = "🟡"
    else:
        mood_icon = "🔴"

    mom_icon = "↗" if (mom is not None and mom > 0) else "↘"
    pulse_icon = "↗" if (pulse is not None and pulse > 0) else "↘"

    # === Current Price ===
    price, change = get_price("BTC-USD")
    if price:
        color = "#22c55e" if change > 0 else "#ef4444"
        st.markdown(
            f"""
            <div style="font-size:22px; font-weight:700; color:white; margin-top:10px;">
                💰 Current Price: ${price:,.2f}
                <span style="color:{color}; font-size:18px; margin-left:8px;">
                    ({change:+.2f}%)
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
    c1, c2, c3, c4 = st.columns(4)

    # Card 1 – Fear & Greed
    with c1:
        val = f"{fear}/100" if fear is not None else "N/A"
        if fear is not None and fear_label:
            if fear > 55:
                col = "#22c55e"
            elif fear > 25:
                col = "#eab308"
            else:
                col = "#ef4444"
            sub = badge(fear_label, col)
        else:
            sub = ""
        st.markdown(
            premium_card("Fear & Greed Index", val, sub, icon=mood_icon),
            unsafe_allow_html=True
        )

    # Card 2 – BTC Dominance
    with c2:
        val = f"{btc_dom:.2f}%" if btc_dom is not None else "N/A"
        st.markdown(
            premium_card("BTC Dominance", val, "Market Strength Indicator", icon="🧲"),
            unsafe_allow_html=True
        )

    # Card 3 – Momentum
    with c3:
        val = f"{mom:.2f}%" if mom is not None else "N/A"
        col = "#22c55e" if (mom is not None and mom > 0) else "#ef4444"
        label = "Bullish" if (mom is not None and mom > 0) else "Bearish"
        sub = badge(label, col)
        st.markdown(
            premium_card("BTC Momentum (7d)", val, sub, icon=mom_icon),
            unsafe_allow_html=True
        )

    # Card 4 – Volume Pulse
    with c4:
        val = f"{pulse:.2f}%" if pulse is not None else "N/A"
        col = "#22c55e" if (pulse is not None and pulse > 0) else "#ef4444"
        label = "High Liquidity" if (pulse is not None and pulse > 0) else "Low Liquidity"
        sub = badge(label, col)
        st.markdown(
            premium_card("Volume Pulse", val, sub, icon=pulse_icon),
            unsafe_allow_html=True
        )

    # Sentiment bar
    score = fear if fear is not None else 50
    st.markdown(
        f"""
        <div class="sentibar-container">
            <div class="sentibar-fill" style="width:{score}%"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
