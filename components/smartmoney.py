import streamlit as st

def render_smartmoney(df):
    st.subheader("💰 Smart Money")

    last = df.iloc[-1]
    prev = df.iloc[-5]

    bias = "BULLISH" if last["close"] > prev["open"] else "BEARISH"

    st.info(f"Smart Money Bias: **{bias}**")
