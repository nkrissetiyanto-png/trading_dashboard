import streamlit as st
import requests
import yfinance as yf


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


def get_coin_momentum(symbol):
    """
    Menghitung momentum coin spesifik (7 hari).
    symbol → BTCUSDT, ETHUSDT, SOLUSDT, dll.
    """
    try:
        ticker = symbol.replace("USDT", "") + "-USD"
        df = yf.download(ticker, period="10d", interval="1d")

        if df.empty or len(df) < 7:
            return None

        df = df.reset_index()
        close = df["Close"]

        change = (close.iloc[-1] - close.iloc[-7]) / close.iloc[-7] * 100
        return round(change, 2)

    except:
        return None


def get_volume_pulse(symbol):
    """
    Mengukur peningkatan penurunan volume coin secara spesifik.
    """
    try:
        ticker = symbol.replace("USDT", "") + "-USD"
        df = yf.download(ticker, period="20d", interval="1d")

        if df.empty:
            return None

        df = df.reset_index()
        vol = df["Volume"]

        pulse = (vol.iloc[-1] - vol.mean()) / vol.mean() * 100
        return round(pulse, 2)
    except:
        return None


def get_btc_dominance(symbol):
    """
    BTC dominance hanya valid jika symbol adalah BTC.
    Untuk coin lain return None.
    """
    if not symbol.startswith("BTC"):
        return None

    try:
        url = "https://api.coingecko.com/api/v3/global"
        data = requests.get(url, timeout=5).json()
        dominance = data["data"]["market_cap_percentage"]["btc"]
        return round(dominance, 2)
    except:
        return None


# ===================== BADGE COMPONENT =====================

def badge(text, color):
    return f"""
    <span style="
        background-color:{color};
        padding:4px 10px;
        border-radius:8px;
        color:white;
        font-size:12px;
        font-weight:600;">
        {text}
    </span>
    """


def premium_card(title, value, subtext="", icon="💠"):
    return f'''
    <div style="padding:18px; border-radius:18px; background:rgba(255,255,255,0.05);
                border:1px solid rgba(255,255,255,0.15); backdrop-filter:blur(10px);
                box-shadow:0 4px 14px rgba(0,0,0,0.25); text-align:center;">
        <div style="font-size:15px; color:#DFE6F0; font-weight:600; margin-bottom:6px;">
            {icon} {title}
        </div>
        <div style="font-size:32px; font-weight:700; color:white; margin-top:-4px;">
            {value}
        </div>
        <div style="font-size:13px; color:#AAB4C2; margin-top:8px;">
            {subtext}
        </div>
    </div>
    '''


# ===================== RENDER PREMIUM SENTIMENT =====================

def render_crypto_sentiment(symbol):
    st.markdown("## 🧭 Crypto Market Sentiment (Premium)")

    # Global indicator
    fear, fear_label = get_fear_greed()

    # Coin-specific indicators
    momentum = get_coin_momentum(symbol)
    pulse = get_volume_pulse(symbol)
    dominance = get_btc_dominance(symbol)

    # Icons
    mood_icon = "🟢" if fear and fear > 55 else "🟡" if fear and fear > 25 else "🔴"
    mom_icon = "↗" if momentum and momentum > 0 else "↘"
    pulse_icon = "↗" if pulse and pulse > 0 else "↘"

    # Layout
    c1, c2, c3, c4 = st.columns(4)

    # Fear & Greed
    with c1:
        val = f"{fear}/100" if fear is not None else "N/A"
        color = "#27ae60" if fear and fear > 55 else "#f1c40f" if fear and fear > 25 else "#c0392b"
        sub = badge(fear_label or "Unknown", color)
        st.markdown(premium_card("Fear & Greed Index", val, subtext=sub, icon=mood_icon), unsafe_allow_html=True)

    # Dominance (only BTC)
    with c2:
        val = f"{dominance:.2f}%" if dominance is not None else "N/A"
        st.markdown(premium_card("BTC Dominance", val, "Market Strength Indicator", icon="🧲"),
                    unsafe_allow_html=True)

    # Momentum
    with c3:
        val = f"{momentum:.2f}%" if momentum is not None else "N/A"
        color = "#2ecc71" if momentum and momentum > 0 else "#e74c3c"
        sub = badge("Bullish" if momentum and momentum > 0 else "Bearish", color)
        st.markdown(premium_card(f"{symbol} Momentum (7d)", val, subtext=sub, icon=mom_icon),
                    unsafe_allow_html=True)

    # Volume Pulse
    with c4:
        val = f"{pulse:.2f}%" if pulse is not None else "N/A"
        color = "#2ecc71" if pulse and pulse > 0 else "#e74c3c"
        sub = badge("High Liquidity" if pulse and pulse > 0 else "Low Liquidity", color)
        st.markdown(premium_card(f"{symbol} Volume Pulse", val, subtext=sub, icon=pulse_icon),
                    unsafe_allow_html=True)

