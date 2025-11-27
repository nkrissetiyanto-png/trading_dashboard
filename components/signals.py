import streamlit as st

def render_signals(df):
    st.subheader("📢 Trade Signals")

    last = df.tail(3)

    buy = last["close"].iloc[-1] > last["EMA20"].iloc[-1] and last["RSI"].iloc[-1] < 70
    sell = last["close"].iloc[-1] < last["EMA20"].iloc[-1] and last["RSI"].iloc[-1] > 30

    if buy:
        st.success("🟢 CONFIRMED BUY")
    elif sell:
        st.error("🔴 CONFIRMED SELL")
    else:
        st.warning("🟡 WAIT / NO SIGNAL")
