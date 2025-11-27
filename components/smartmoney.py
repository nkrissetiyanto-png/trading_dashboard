import streamlit as st

def render_smartmoney(df):
    st.subheader("💰 Smart Money Concept")

    last = df.tail(1).iloc[0]

    status = "BULLISH" if last['close'] > df['open'].iloc[-5] else "BEARISH"

    st.info(f"Smart Money Status: **{status}**")
