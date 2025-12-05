import streamlit as st
import yfinance as yf
import pandas as pd

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
    "Energy": ["ADRO.JK","BYAN.JK"]
}

def get_stock_sentiment(symbol):
    df = yf.download(symbol, period="30d", interval="1d")
    if df.empty:
        return None

    df = df.reset_index()

    # Kalau datanya kurang dari 7 hari → tidak bisa hitung momentum
    if len(df) < 7:
        return None

    close = df["Close"]

    # Trend score (EMA 5 vs EMA 20)
    df["EMA5"] = close.ewm(span=5).mean()
    df["EMA20"] = close.ewm(span=20).mean()
    trend_score = 20 if df["EMA5"].iloc[-1] > df["EMA20"].iloc[-1] else 5

    # Momentum 5 hari (aman dari NaN & Series)
    try:
        mom = float((close.iloc[-1] - close.iloc[-6]) / close.iloc[-6] * 100)
    except:
        mom = 0.0
    mom_score = min(max(mom + 10, 0), 20)

    # Volatility score
    vol = close.pct_change().std() * 100
    vol_score = 20 - min(vol, 20)

    # Volume pressure
    try:
        vp = (df["Volume"].iloc[-1] - df["Volume"].mean()) / df["Volume"].mean() * 100
        vp = float(vp)
    except:
        vp = 0
    vp_score = min(max(vp + 10, 0), 20)

    # Total score
    total = trend_score + mom_score + vol_score + vp_score
    total = max(0, min(total, 100))

    return round(total)
    
def get_stock_sentiment(symbol):
    df = yf.download(symbol, period="20d", interval="1d")
    if df.empty:
        return None

    df = df.reset_index()

    # Trend
    df["EMA5"] = df["Close"].ewm(span=5).mean()
    df["EMA20"] = df["Close"].ewm(span=20).mean()

    trend_score = 20 if df["EMA5"].iloc[-1] > df["EMA20"].iloc[-1] else 5

    # Momentum (5-day change)
    mom = (df["Close"].iloc[-1] - df["Close"].iloc[-6]) / df["Close"].iloc[-6] * 100
    mom_score = min(max(mom + 10, 0), 20)

    # Volatility
    vol = df["Close"].pct_change().std() * 100
    vol_score = 20 - min(vol, 20)

    # Volume Pressure
    vp = (df["Volume"].iloc[-1] - df["Volume"].mean()) / df["Volume"].mean() * 100
    vp_score = min(max(vp + 10, 0), 20)

    total = trend_score + mom_score + vol_score + vp_score
    total = max(0, min(total, 100))

    return round(total)

def get_sentiment_index():
    df = yf.download("^JKSE", period="10d", interval="1d")

    if df.empty:
        return None
    
    df = df.reset_index()
    df["change"] = df["Close"].pct_change() * 100

    if pd.isna(df["change"].iloc[-1]):
        change_val = 0.0
    else:
        change_val = float(df["change"].iloc[-1])

    return {
        "change": round(change_val, 2),
        "close": round(float(df["Close"].iloc[-1]), 2)
    }

def get_sector_strength():
    changes = []

    for symbol in LQ45:
        try:
            df = yf.download(symbol, period="3d", interval="1d")

            if df.empty or "Close" not in df.columns:
                continue

            df = df.reset_index()

            if len(df) < 2:
                continue

            prev_close = float(df["Close"].iloc[-2])
            last_close = float(df["Close"].iloc[-1])

            if prev_close <= 0:
                continue

            pct_change = ((last_close - prev_close) / prev_close) * 100

            # Pastikan hasilnya float valid
            pct_change = float(pct_change)

            changes.append(pct_change)

        except Exception:
            continue

    # Jika tidak ada data valid
    if len(changes) == 0:
        return None

    avg_change = sum(changes) / len(changes)

    # Skala menjadi 0–100
    score = (avg_change + 5) * 10
    score = max(0, min(score, 100))

    return round(score)

def render_sentiment(symbol):
    st.subheader("🧭 Sentimen Pasar Indonesia")

    # Market sentiment
    idx = get_sentiment_index()
    market_score = get_sector_strength()

    # Jika market gagal → stop
    if idx is None or market_score is None:
        st.warning("Tidak dapat memuat sentimen pasar.")
        return

    # Sector sentiment
    sector, sector_score = get_sector_sentiment(symbol)

    # Stock sentiment
    stock_score = get_stock_sentiment(symbol)

    # Tentukan mood dari market
    if market_score >= 70:
        mood = "🟢 Bullish"
    elif market_score >= 40:
        mood = "🟡 Netral"
    else:
        mood = "🔴 Bearish"

    # ==== UI ====
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Market Sentiment", f"{market_score}/100", mood)

    with col2:
        if sector_score is not None:
            st.metric(f"{sector} Sector", f"{sector_score}/100")
        else:
            st.metric("Sector", "N/A")

    with col3:
        if stock_score is not None:
            st.metric(f"{symbol} Sentiment", f"{stock_score}/100")
        else:
            st.metric("Stock", "N/A")

    # Progress bar for market sentiment
    st.progress(market_score)

