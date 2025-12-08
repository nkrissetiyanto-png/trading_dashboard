import streamlit as st

def render_smartmoney(df):
    st.subheader("💰 Smart Money")

    last = df.iloc[-1]
    prev = df.iloc[-5]

    bias = "BULLISH" if last["close"] > prev["open"] else "BEARISH"

    st.info(f"Smart Money Bias: **{bias}**")

def get_smart_money_bias(df):
    """
    Return simple smart money bias:
    - Bullish jika close > EMA50
    - Bearish jika close < EMA50
    """
    import pandas as pd

    df = df.copy()
    df["ema50"] = df["Close"].ewm(span=50).mean()

    if df["Close"].iloc[-1] > df["ema50"].iloc[-1]:
        return "BULLISH"
    else:
        return "BEARISH"
