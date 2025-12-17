import streamlit as st
import pandas as pd
import numpy as np

# ===============================
# INDICATORS (LOCAL, SAFE)
# ===============================

def EMA(series, period):
    return series.ewm(span=period, adjust=False).mean()

def RSI(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ===============================
# MAIN SIGNAL ENGINE
# ===============================

def render_signals(df: pd.DataFrame):
    st.subheader("📣 Trade Signals")

    if df is None or df.empty or len(df) < 30:
        st.warning("Data tidak cukup untuk generate signal.")
        return

    df = df.copy()

    # --- SAFETY NORMALIZATION ---
    if "close" not in df.columns:
        st.error("Kolom 'close' tidak ditemukan.")
        return

    # --- CALCULATE INDICATORS ---
    df["EMA20"] = EMA(df["close"], 20)
    df["RSI"] = RSI(df["close"])

    last = df.iloc[-1]

    # --- SIGNAL LOGIC ---
    buy_signal = (
        last["close"] > last["EMA20"]
        and last["RSI"] < 70
    )

    sell_signal = (
        last["close"] < last["EMA20"]
        and last["RSI"] > 30
    )

    # ===============================
    # UI OUTPUT
    # ===============================

    if buy_signal:
        st.success("🟢 **BUY SIGNAL CONFIRMED**")
        st.markdown(
            f"""
            **Reason:**
            - Price above EMA20
            - RSI masih sehat ({last["RSI"]:.1f})
            """
        )

    elif sell_signal:
        st.error("🔴 **SELL SIGNAL CONFIRMED**")
        st.markdown(
            f"""
            **Reason:**
            - Price below EMA20
            - RSI melemah ({last["RSI"]:.1f})
            """
        )

    else:
        st.info("⚪ **NO CLEAR SIGNAL**")
        st.markdown(
            f"""
            **Market Status:**
            - Close: {last["close"]:.2f}
            - EMA20: {last["EMA20"]:.2f}
            - RSI: {last["RSI"]:.1f}
            """
        )
