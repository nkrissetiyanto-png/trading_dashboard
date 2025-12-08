import streamlit as st
import numpy as np
import pandas as pd


def calc_reversal(df: pd.DataFrame):
    df = df.copy()

    if df is None or len(df) < 25:
        return 0, "N/A", ["Data terlalu sedikit untuk analisa reversal."]

    required = ["Open", "High", "Low", "Close", "Volume"]
    for col in required:
        if col not in df.columns:
            return 0, "N/A", [f"Kolom {col} tidak tersedia."]

    # ========== RSI Proxy ==========
    df["chg"] = df["Close"].diff()
    df["up"] = df["chg"].clip(lower=0)
    df["dn"] = -df["chg"].clip(upper=0)

    avg_up = df["up"].rolling(14).mean()
    avg_dn = df["dn"].rolling(14).mean()

    with np.errstate(divide="ignore", invalid="ignore"):
        rs = avg_up / avg_dn
        rsi = 100 - (100 / (1 + rs))

    last_rsi = rsi.iloc[-1]
    if np.isnan(last_rsi):
        last_rsi = 50

    # ========== Candle Body ==========
    o = df["Open"].iloc[-1]
    c = df["Close"].iloc[-1]

    body_pct = ((c - o) / o * 100) if o != 0 else 0.0

    # ========== Volume Spike ==========
    vol = df["Volume"]
    vol_ma = vol.rolling(20).mean().iloc[-1]
    vol_last = vol.iloc[-1]

    if vol_ma and not np.isnan(vol_ma):
        vol_ratio = vol_last / vol_ma
    else:
        vol_ratio = 1.0

    signals = []
    score = 0

    # RSI
    if last_rsi < 30:
        signals.append("RSI Oversold → potensi Reversal UP.")
        score += 2
    elif last_rsi > 70:
        signals.append("RSI Overbought → potensi Reversal DOWN.")
        score -= 2
    else:
        signals.append("RSI di zona netral.")

    # Candle Body
    if body_pct > 1:
        signals.append("Candle bullish kuat → mendukung Reversal UP.")
        score += 1
    elif body_pct < -1:
        signals.append("Candle bearish kuat → mendukung Reversal DOWN.")
        score -= 1
    else:
        signals.append("Body candle kecil → sinyal lemah.")

    # Volume
    if vol_ratio > 1.3:
        if body_pct > 0:
            signals.append("Volume spike pada candle hijau → tekanan beli kuat.")
            score += 1
        elif body_pct < 0:
            signals.append("Volume spike pada candle merah → tekanan jual kuat.")
            score -= 1
        else:
            signals.append("Volume spike tetapi body netral.")
    else:
        signals.append("Volume normal → tidak ada dorongan besar.")

    prob = int(min(100, max(0, (score + 3) * 20)))
    direction = "UP" if prob >= 55 else "DOWN"

    return prob, direction, signals


def render_reversal_probability(df: pd.DataFrame):
    st.markdown("### 🔄 Reversal Probability (Saham Indonesia)")

    prob, direction, signals = calc_reversal(df)

    if direction == "N/A":
        st.info("Tidak cukup data untuk analisis reversal.")
        for s in signals:
            st.markdown(f"- {s}")
        st.markdown("---")
        return

    color = "🟢" if direction == "UP" else "🔴"

    st.markdown(f"**{color} Reversal Probability: {prob}% → {direction}**")
    st.markdown("#### 📘 Penjelasan AI:")

    for s in signals:
        st.markdown(f"- {s}")

    st.markdown("---")
