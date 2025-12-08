import streamlit as st
import yfinance as yf
import requests
import numpy as np
import pandas as pd

# ============================================================
# ===============   SAFETY HELPERS   =========================
# ============================================================

def _safe_num(x):
    try:
        x = float(str(x).replace("%","").replace("$","").strip())
        if np.isnan(x):
            return None
        return x
    except:
        return None


# ============================================================
# ===============   MARKET / SECTOR SENTIMENT   ==============
# ============================================================

SECTOR_MAP = {
    "BBRI.JK": "Finance",
    "BBCA.JK": "Finance",
    "BMRI.JK": "Finance",
    "BBNI.JK": "Finance",

    "TLKM.JK": "Telco",
    "ISAT.JK": "Telco",
    "EXCL.JK": "Telco",

    "ASII.JK": "Automotive",
    "UNVR.JK": "Consumer",
    "ICBP.JK": "Consumer",
    "INDF.JK": "Consumer",
}


def get_sector_sentiment(symbol):
    """
    Hitung sentimen sektor berdasarkan saham-saham dalam sektor yang sama.
    Jika sektor tidak ditemukan → netral (50).
    """

    sector = SECTOR_MAP.get(symbol.upper(), "Unknown")

    # Jika sektor tidak dikenal
    if sector == "Unknown":
        return "Unknown", 50

    # Ambil semua saham dalam sektor
    peers = [s for s, sec in SECTOR_MAP.items() if sec == sector]

    scores = []
    for s in peers:
        try:
            df = yf.download(s, period="7d", interval="1d")
            if df.empty or len(df) < 2:
                continue
            close = df["Close"].dropna()
            chg = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100
            scores.append(chg)
        except:
            continue

    if len(scores) == 0:
        return sector, 50

    avg_score = np.mean(scores)

    # Scale ke 0–100
    scaled = np.clip(round(avg_score + 50), 0, 100)

    return sector, scaled


# ============================================================
# ===============   ADVANCED FOREIGN FLOW (ANTI-BIAS) ========
# ============================================================

def get_eido_change():
    """Primary: EIDO daily close change (anti-bias)."""
    try:
        df = yf.download("EIDO", period="5d", interval="1d")
        if df.empty or len(df) < 2:
            return None

        close = df["Close"].dropna()
        if len(close) < 2:
            return None

        last = close.iloc[-1]
        prev = close.iloc[-2]
        return round((last - prev) / prev * 100, 2)
    except:
        return None


def get_nasdaq_eido_change():
    """Fallback: NASDAQ API — selalu ada data meski weekend."""
    try:
        url = "https://api.nasdaq.com/api/quote/EIDO/info?assetclass=stocks"
        headers = {"User-Agent": "Mozilla/5.0"}
        data = requests.get(url, headers=headers, timeout=5).json()

        info = data.get("data", {}).get("primaryData", {})
        last = _safe_num(info.get("lastSalePrice", ""))
        prev = _safe_num(info.get("previousClose", ""))

        if last is None or prev is None:
            return None

        return round((last - prev) / prev * 100, 2)
    except:
        return None


def get_eem_change():
    """Proxy ETF EEM (Emerging Markets ETF)."""
    try:
        df = yf.download("EEM", period="5d", interval="1d")
        if df.empty or len(df) < 2:
            return None
        close = df["Close"].dropna()
        last = close.iloc[-1]
        prev = close.iloc[-2]
        return round((last - prev) / prev * 100, 2)
    except:
        return None


def get_foreign_flow_sentiment():
    """
    FINAL Foreign Flow (Anti-bias, stable, never NaN)
    Priority:
    1) EIDO daily close
    2) NASDAQ lastSalePrice
    3) EEM proxy
    """

    eido = get_eido_change()
    if eido is not None:
        return eido, "EIDO (Primary)"

    nasdaq = get_nasdaq_eido_change()
    if nasdaq is not None:
        return nasdaq, "NASDAQ (Fallback)"

    eem = get_eem_change()
    if eem is not None:
        return eem, "EEM Proxy"

    return None, "No Data"


# ============================================================
# ===============   IHSG SENTIMENT SECTION ===================
# ============================================================

def get_ihsg_sentiment():
    try:
        df = yf.download("^JKSE", period="7d", interval="1d")
        if df.empty or len(df) < 2:
            return None
        close = df["Close"].dropna()
        chg = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100
        return round(chg, 2)
    except:
        return None


# ============================================================
# ===============   RENDER SENTIMENT UI ======================
# ============================================================

def render_sentiment(symbol):
    st.markdown("## 🧭 Market Sentiment — Indonesia")

    # ---------------------------------------------------------
    # 1. IHSG SENTIMENT
    # ---------------------------------------------------------
    ihsg = get_ihsg_sentiment()
    if ihsg is None:
        st.warning("IHSG data unavailable")
    else:
        color = "🟢" if ihsg > 0 else "🔴"
        st.markdown(f"### {color} IHSG: {ihsg:.2f}%")

    # ---------------------------------------------------------
    # 2. SECTOR SENTIMENT
    # ---------------------------------------------------------
    sector, score = get_sector_sentiment(symbol)
    st.markdown(f"### 🏭 Sector: **{sector}** — Score: **{score}/100**")

    # ---------------------------------------------------------
    # 3. FOREIGN FLOW SENTIMENT (ANTI-BIAS)
    # ---------------------------------------------------------
    eido_chg, source = get_foreign_flow_sentiment()

    if eido_chg is None:
        st.warning("Foreign Flow data unavailable.")
    else:
        color = "🟢" if eido_chg > 0 else "🔴"
        st.markdown(f"### 🌏 Foreign Flow: {color} {eido_chg:.2f}%  — *{source}*")

    # ---------------------------------------------------------
    # 4. STOCK-SPECIFIC MOMENTUM
    # ---------------------------------------------------------
    try:
        df = yf.download(symbol, period="7d", interval="1d")
        if not df.empty and len(df) > 2:
            close = df["Close"].dropna()
            change = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100
            st.markdown(f"### 📈 {symbol} Momentum: {change:.2f}%")
    except:
        pass

    st.markdown("---")
