import streamlit as st
import yfinance as yf
import pandas as pd

# ============================================================
#  🔷 Konfigurasi Saham & Sektor
# ============================================================

LQ45 = [
    "BBCA.JK","BBRI.JK","BMRI.JK","BBNI.JK","ASII.JK","TLKM.JK",
    "UNVR.JK","ICBP.JK","INDF.JK","AMRT.JK"
]

SECTOR_MAP = {
    "BBRI.JK": "Finance",
    "BBCA.JK": "Finance",
    "BMRI.JK": "Finance",
    "BBNI.JK": "Finance",

    "TLKM.JK": "Telco",
    "ISAT.JK": "Telco",

    "ASII.JK": "Automotive",
    "UNTR.JK": "Automotive",

    "UNVR.JK": "Consumer",
    "ICBP.JK": "Consumer",
    "INDF.JK": "Consumer",

    "ADRO.JK": "Energy",
    "BYAN.JK": "Energy",
}

SECTOR_COMPONENTS = {
    "Finance": ["BBRI.JK","BBCA.JK","BMRI.JK","BBNI.JK"],
    "Telco": ["TLKM.JK","ISAT.JK"],
    "Automotive": ["ASII.JK","UNTR.JK"],
    "Consumer": ["UNVR.JK","ICBP.JK","INDF.JK"],
    "Energy": ["ADRO.JK","BYAN.JK"],
}

# ============================================================
#  🔷 Fungsi Sentimen Saham
# ============================================================

def get_stock_sentiment(symbol):
    df = yf.download(symbol, period="30d", interval="1d")
    if df.empty:
        return None

    df = df.reset_index()
    if len(df) < 7:
        return None

    close = df["Close"]

    df["EMA5"] = close.ewm(span=5).mean()
    df["EMA20"] = close.ewm(span=20).mean()
    trend_score = 20 if df["EMA5"].iloc[-1] > df["EMA20"].iloc[-1] else 5

    try:
        mom = float((close.iloc[-1] - close.iloc[-6]) / close.iloc[-6] * 100)
    except:
        mom = 0
    mom_score = min(max(mom + 10, 0), 20)

    vol = close.pct_change().std() * 100
    vol_score = 20 - min(vol, 20)

    try:
        vp = float((df["Volume"].iloc[-1] - df["Volume"].mean()) / df["Volume"].mean() * 100)
    except:
        vp = 0
    vp_score = min(max(vp + 10, 0), 20)

    total = trend_score + mom_score + vol_score + vp_score
    return max(0, min(int(total), 100))


# ============================================================
#  🔷 Fungsi Sentimen Sektor
# ============================================================

def get_sector_sentiment(symbol):
    sector = SECTOR_MAP.get(symbol)
    if sector is None:
        return None, None

    tickers = SECTOR_COMPONENTS.get(sector, [])
    if not tickers:
        return sector, None

    changes = []
    for t in tickers:
        df = yf.download(t, period="5d", interval="1d")
        if df.empty:
            continue

        df = df.reset_index()
        if len(df) < 2:
            continue

        prev = float(df["Close"].iloc[-2])
        last = float(df["Close"].iloc[-1])
        if prev <= 0:
            continue

        pct = (last - prev) / prev * 100
        changes.append(pct)

    if len(changes) == 0:
        return sector, None

    avg = sum(changes) / len(changes)
    score = (avg + 5) * 10
    return sector, max(0, min(round(score), 100))


# ============================================================
#  🔷 Fungsi IHSG Index Sentiment
# ============================================================

def get_sentiment_index():
    df = yf.download("^JKSE", period="10d", interval="1d")
    if df.empty:
        return None

    df = df.reset_index()
    df["change"] = df["Close"].pct_change() * 100

    change = df["change"].iloc[-1]
    if pd.isna(change):
        change = 0

    return {
        "change": round(float(change), 2),
        "close": round(float(df["Close"].iloc[-1]), 2)
    }


# ============================================================
#  🔷 Market Strength (LQ45)
# ============================================================

def get_sector_strength():
    changes = []
    for sym in LQ45:
        try:
            df = yf.download(sym, period="3d", interval="1d")
            if df.empty or "Close" not in df.columns:
                continue

            df = df.reset_index()
            if len(df) < 2:
                continue

            prev = float(df["Close"].iloc[-2])
            last = float(df["Close"].iloc[-1])
            pct = (last - prev) / prev * 100
            changes.append(pct)
        except:
            continue

    if len(changes) == 0:
        return None

    avg = sum(changes) / len(changes)
    return max(0, min(round((avg + 5) * 10), 100))


# ============================================================
#  🔷 Render Sentimen UI
# ============================================================

def render_sentiment(symbol):
    st.subheader("🧭 Sentimen Pasar Indonesia")

    ihsg = get_sentiment_index()
    market_score = get_sector_strength()

    if ihsg is None or market_score is None:
        st.warning("Tidak dapat memuat sentimen pasar.")
        return

    sector, sector_score = get_sector_sentiment(symbol)
    stock_score = get_stock_sentiment(symbol)

    if market_score >= 70:
        mood = "🟢 Bullish"
    elif market_score >= 40:
        mood = "🟡 Netral"
    else:
        mood = "🔴 Bearish"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Market Sentiment", f"{market_score}/100", mood)

    with col2:
        st.metric(f"{sector} Sector" if sector_score else "Sector", 
                  f"{sector_score}/100" if sector_score else "N/A")

    with col3:
        st.metric(f"{symbol} Sentiment", 
                  f"{stock_score}/100" if stock_score else "N/A")

    st.progress(market_score)
