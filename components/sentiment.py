import streamlit as st
import yfinance as yf
import pandas as pd

LQ45 = [
    "BBCA.JK","BBRI.JK","BMRI.JK","BBNI.JK","ASII.JK","TLKM.JK",
    "UNVR.JK","ICBP.JK","INDF.JK","AMRT.JK"
]

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
        df = yf.download(symbol, period="3d", interval="1d")

        if df.empty:
            continue

        df = df.reset_index()

        if len(df) < 2:  # tidak ada data cukup
            continue

        prev = df["Close"].iloc[-2]
        now = df["Close"].iloc[-1]

        try:
            pct = (now - prev) / prev * 100
        except:
            pct = 0

        changes.append(pct)

    if len(changes) == 0:
        return None

    avg_change = sum(changes) / len(changes)

    # Scale menjadi 0–100
    score = round((avg_change + 5) * 10)
    score = max(0, min(score, 100))

    return score


def render_sentiment():
    st.subheader("🧭 Sentimen Pasar Indonesia")

    idx = get_sentiment_index()
    score = get_sector_strength()

    if idx is None or score is None:
        st.warning("Tidak dapat memuat sentimen pasar.")
        return

    if score >= 70:
        mood = "🟢 Bullish"
    elif score >= 40:
        mood = "🟡 Netral"
    else:
        mood = "🔴 Bearish"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("IHSG", idx["close"])

    with col2:
        st.metric("Perubahan Harian", f"{idx['change']}%")

    with col3:
        st.metric("Sentimen", f"{score}/100", mood)

    st.progress(score)
