import streamlit as st
import yfinance as yf
import pandas as pd

# Daftar saham LQ45 (contoh; bisa diperbarui)
LQ45 = [
    "BBCA.JK","BBRI.JK","BMRI.JK","BBNI.JK","ASII.JK","TLKM.JK",
    "ARTO.JK","AMRT.JK","UNVR.JK","BRIS.JK","BYAN.JK","ICBP.JK",
    "INDF.JK","MDKA.JK","PGAS.JK","PTPP.JK","TOWR.JK"
]

def get_sentiment_index():
    # Ambil data IHSG 10 hari terakhir
    df = yf.download("^JKSE", period="10d", interval="1d")

    if df.empty:
        return None

    # Pastikan kolom Close ada
    if "Close" not in df.columns:
        return None

    # Hitung persentase perubahan harian
    change_series = df["Close"].pct_change() * 100

    # Ambil nilai terakhir
    last_change = change_series.iloc[-1]
    last_close = df["Close"].iloc[-1]

    # Handle NaN / non-numeric
    try:
        change_val = float(last_change)
    except Exception:
        change_val = 0.0

    try:
        close_val = float(last_close)
    except Exception:
        return None

    return {
        "change": round(change_val, 2),
        "close": round(close_val, 2),
    }

def get_sector_strength():
    changes = []

    for symbol in LQ45:
        df = yf.download(symbol, period="2d", interval="1d")
        if df.empty:
            continue
        df = df.reset_index()
        change = (df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2] * 100
        changes.append(change)

    if len(changes) == 0:
        return None

    avg_change = sum(changes) / len(changes)

    sentiment_score = round((avg_change + 5) * 10)  # convert to 0–100 scale

    sentiment_score = max(0, min(sentiment_score, 100))

    return sentiment_score

def render_sentiment():
    st.subheader("🧭 Sentimen Pasar Indonesia")

    idx = get_sentiment_index()
    score = get_sector_strength()
    
    if idx is None or score is None:
        st.warning("Tidak dapat memuat sentimen pasar (data tidak valid).")
        return

    # Warna berdasarkan score
    if score >= 70: mood = "🟢 Bullish"
    elif score >= 40: mood = "🟡 Neutral"
    else: mood = "🔴 Bearish"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("IHSG Close", idx["close"])

    with col2:
        st.metric("IHSG Change", f"{idx['change']}%")

    with col3:
        st.metric("Market Sentiment", f"{score}/100", mood)

    st.progress(score)
