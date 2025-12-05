import streamlit as st
import requests
import yfinance as yf
import pandas as pd

# ============= API FUNCTIONS ==================

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
        dominance = data["data"]["market_cap_percentage"]["btc"]
        return round(dominance, 2)
    except:
        return None

def get_btc_momentum():
    df = yf.download("BTC-USD", period="10d", interval="1d")
    if df.empty or len(df) < 7:
        return None

    df = df.reset_index()
    close = df["Close"]

    try:
        change = (close.iloc[-1] - close.iloc[-7]) / close.iloc[-7] * 100
        return round(change, 2)
    except:
        return None

def get_volume_pulse():
    df = yf.download("BTC-USD", period="15d", interval="1d")
    if df.empty:
        return None

    df = df.reset_index()
    vol = df["Volume"]

    try:
        pulse = (vol.iloc[-1] - vol.mean()) / vol.mean() * 100
        return round(pulse, 2)
    except:
        return None


# ============= BADGE COMPONENT ==================

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
        <div style="font-size:34px; font-weight:700; color:white; margin-top:-4px;">
            {value}
        </div>
        <div style="font-size:13px; color:#AAB4C2; margin-top:8px;">
            {subtext}
        </div>
    </div>
    '''

def is_number(x):
    try:
        float(x)
        return True
    except:
        return False

def is_pos(x):
    return is_number(x) and float(x) > 0

# ============= PREMIUM RENDER ==================
def render_crypto_sentiment():

    st.markdown("## 🧭 Crypto Market Sentiment (Premium)")

    fear, fear_label = get_fear_greed()
    btc_dom = get_btc_dominance()
    mom = get_btc_momentum()
    pulse = get_volume_pulse()

    # --- pastikan mom & pulse scalar float / None ---
    try:
        mom = float(mom) if mom is not None else None
    except:
        mom = None

    try:
        pulse = float(pulse) if pulse is not None else None
    except:
        pulse = None

    # --- Icon & arah ---
    mood_icon = "🟢" if fear is not None and fear > 55 else "🟡" if fear is not None and fear > 25 else "🔴"
    mom_icon = "↗" if (mom is not None and mom > 0) else "↘"
    pulse_icon = "↗" if (pulse is not None and pulse > 0) else "↘"

    # --- Layout ---
    c1, c2, c3, c4 = st.columns(4)

    # Fear & Greed
    with c1:
        val = f"{fear}/100" if fear is not None else "N/A"
        if fear is not None and fear_label:
            if fear > 55:
                fg_color = "#27ae60"
            elif fear > 25:
                fg_color = "#f1c40f"
            else:
                fg_color = "#c0392b"
            sub = badge(fear_label, fg_color)      # ⬅️ TIDAK ada + "</div>"
        else:
            sub = ""
        st.markdown(
            premium_card("Fear & Greed Index", val, sub, icon=mood_icon),
            unsafe_allow_html=True
        )

    # BTC Dominance
    with c2:
        val = f"{btc_dom:.2f}%" if btc_dom is not None else "N/A"
        st.markdown(premium_card("BTC Dominance", val, "Market Strength Indicator", icon="🧲"),
                    unsafe_allow_html=True)

    # Momentum
    with c3:
        val = f"{mom:.2f}%" if mom is not None else "N/A"
        color = "#2ecc71" if (mom is not None and mom > 0) else "#e74c3c"
        sub = badge("Bullish" if mom is not None and mom > 0 else "Bearish", color)  # ⬅️ tanpa tambahan apa pun
        st.markdown(
            premium_card("BTC Momentum (7d)", val, sub, icon=mom_icon),
            unsafe_allow_html=True
        )

    # Volume Pulse
    with c4:
        val = f"{pulse:.2f}%" if pulse is not None else "N/A"
        color = "#2ecc71" if (pulse is not None and pulse > 0) else "#e74c3c"
        sub = badge("High Liquidity" if pulse is not None and pulse > 0 else "Low Liquidity", color)
        st.markdown(
            premium_card("Volume Pulse", val, sub, icon=pulse_icon),
            unsafe_allow_html=True
        )

    # ===== Progress Sentiment Bar =====
    score = fear if fear is not None else 50
    st.markdown("""
        <style>
        .premium-bar {
            width:100%;
            height:20px;
            background:#1f1f1f;
            border-radius:10px;
            overflow:hidden;
            margin-top:15px;
            border:1px solid rgba(255,255,255,0.15);
        }
        .premium-fill {
            height:100%;
            background:linear-gradient(90deg, #2ecc71, #f1c40f, #e74c3c);
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="premium-bar">
            <div class="premium-fill" style="width:{score}%"></div>
        </div>
    """, unsafe_allow_html=True)
