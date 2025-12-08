import streamlit as st
import requests
import yfinance as yf
import numpy as np
import pandas as pd


# ===================== HELPERS =====================

def _safe_float(x):
    """Konversi apa pun ke float scalar, atau None jika gagal."""
    try:
        if isinstance(x, (list, tuple, np.ndarray)):
            if len(x) == 0:
                return None
            x = x[-1]
        if isinstance(x, pd.Series):
            if len(x) == 0:
                return None
            x = x.iloc[-1]
        if x is None:
            return None
        x = float(x)
        if np.isnan(x):
            return None
        return x
    except Exception:
        return None


# ===================== API FUNCTIONS =====================

def get_fear_greed():
    try:
        url = "https://api.alternative.me/fng/?limit=1&format=json"
        data = requests.get(url, timeout=5).json()
        value = int(data["data"][0]["value"])
        rating = data["data"][0]["value_classification"]
        return value, rating
    except Exception:
        return None, None


def get_coin_momentum(symbol: str):
    """Momentum 7 hari untuk coin spesifik (BTCUSDT, ETHUSDT, dll)."""
    try:
        ticker = symbol.replace("USDT", "") + "-USD"
        df = yf.download(ticker, period="10d", interval="1d")

        if df.empty or len(df) < 7:
            return None

        close = df["Close"].astype(float)
        change = (close.iloc[-1] - close.iloc[-7]) / close.iloc[-7] * 100
        return round(float(change), 2)
    except Exception:
        return None


def get_volume_pulse(symbol: str):
    """Volume pulse terhadap rata-rata ~20 hari."""
    try:
        ticker = symbol.replace("USDT", "") + "-USD"
        df = yf.download(ticker, period="20d", interval="1d")

        if df.empty:
            return None

        vol = df["Volume"].astype(float)
        base = vol.mean()
        if base == 0 or np.isnan(base):
            return None

        pulse = (vol.iloc[-1] - base) / base * 100
        return round(float(pulse), 2)
    except Exception:
        return None


def get_btc_dominance(symbol: str):
    """BTC dominance hanya relevan bila symbol diawali BTC."""
    if not symbol.upper().startswith("BTC"):
        return None

    try:
        url = "https://api.coingecko.com/api/v3/global"
        data = requests.get(url, timeout=5).json()
        dominance = data["data"]["market_cap_percentage"]["btc"]
        return round(float(dominance), 2)
    except Exception:
        return None


# ===================== UI COMPONENTS =====================

def badge(text, color):
    return f"""<span style="background-color:{color}; padding:4px 10px; border-radius:8px; color:white; font-size:12px; font-weight:600; display:inline-block;">{text}</span>"""


def premium_card(title, value, sub_html="", icon="💠"):
    return f"""
    <div style="
        padding:18px;
        border-radius:18px;
        background:rgba(255,255,255,0.05);
        border:1px solid rgba(255,255,255,0.15);
        backdrop-filter:blur(10px);
        box-shadow:0 4px 14px rgba(0,0,0,0.25);
        text-align:center;
    ">
        <p style="font-size:15px; color:#DFE6F0; font-weight:600; margin-bottom:6px;">
            {icon} {title}
        </p>
        <p style="font-size:32px; font-weight:700; color:white; margin-top:-4px;">
            {value}
        </p>
        <div style="font-size:13px; color:#AAB4C2; margin-top:8px;">
            {sub_html}
        </div>
    </div>
    """

# ===================== RENDER PREMIUM SENTIMENT =====================

def render_crypto_sentiment(symbol: str):
    st.subheader("🧭 Crypto Market Sentiment (Premium)")

    # ---- Ambil data mentah ----
    fear_raw, fear_label = get_fear_greed()
    momentum_raw = get_coin_momentum(symbol)
    pulse_raw = get_volume_pulse(symbol)
    dominance_raw = get_btc_dominance(symbol)

    # ---- Normalisasi ke scalar float / None ----
    fear = _safe_float(fear_raw)
    momentum = _safe_float(momentum_raw)
    pulse = _safe_float(pulse_raw)
    dominance = _safe_float(dominance_raw)

    # ---- Icon logic aman ----
    if fear is None:
        mood_icon = "⚪️"
    elif fear > 55:
        mood_icon = "🟢"
    elif fear > 25:
        mood_icon = "🟡"
    else:
        mood_icon = "🔴"

    mom_icon = "↗" if (momentum is not None and momentum > 0) else "↘"
    pulse_icon = "↗" if (pulse is not None and pulse > 0) else "↘"

    # ---- Layout ----
    c1, c2, c3, c4 = st.columns(4)

    # === CARD 1: Fear & Greed ===
    with c1:
        val = f"{int(fear)}/100" if fear is not None else "N/A"
        if fear is not None:
            if fear > 55:
                col = "#27ae60"
            elif fear > 25:
                col = "#f1c40f"
            else:
                col = "#c0392b"
        else:
            col = "#7f8c8d"

        sub = badge(fear_label or "Unknown", col)
        html = premium_card("Fear & Greed Index", val, sub_html=sub, icon=mood_icon)
        st.markdown(html, unsafe_allow_html=True)

    # === CARD 2: BTC Dominance (hanya BTC) ===
    with c2:
        val = f"{dominance:.2f}%" if dominance is not None else "N/A"
        html = premium_card("BTC Dominance", val, "Market Strength Indicator", icon="🧲")
        st.markdown(html, unsafe_allow_html=True)

    # === CARD 3: Coin Momentum ===
    with c3:
        val = f"{momentum:.2f}%" if momentum is not None else "N/A"
        col = "#2ecc71" if (momentum is not None and momentum > 0) else "#e74c3c"
        sub = badge(
            "Bullish" if (momentum is not None and momentum > 0) else "Bearish",
            col,
        )
        title = f"{symbol} Momentum (7d)"
        html = premium_card(title, val, sub_html=sub, icon=mom_icon)
        st.markdown(html, unsafe_allow_html=True)

    # === CARD 4: Volume Pulse ===
    with c4:
        val = f"{pulse:.2f}%" if pulse is not None else "N/A"
        col = "#2ecc71" if (pulse is not None and pulse > 0) else "#e74c3c"
        sub = badge(
            "High Liquidity"
            if (pulse is not None and pulse > 0)
            else "Low Liquidity",
            col,
        )
        title = f"{symbol} Volume Pulse"
        html = premium_card(title, val, sub_html=sub, icon=pulse_icon)
        st.markdown(html, unsafe_allow_html=True)
