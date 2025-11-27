import streamlit as st
import pandas as pd
import numpy as np

def EMA(series, period):
    return series.ewm(span=period, adjust=False).mean()

def RSI(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(span=period).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(span=period).mean()
    RS = gain / loss
    return 100 - (100 / (1 + RS))

def MACD(series):
    exp1 = EMA(series, 12)
    exp2 = EMA(series, 26)
    macd = exp1 - exp2
    signal = EMA(macd, 9)
    return macd, signal

def render_indicators(df):
    st.subheader("📊 Technical Indicators")

    df["EMA20"] = EMA(df["close"], 20)
    df["RSI"] = RSI(df["close"])
    df["MACD"], df["MACD_SIGNAL"] = MACD(df["close"])

    st.line_chart(df[["close", "EMA20"]])
    st.line_chart(df[["RSI"]])
    st.line_chart(df[["MACD", "MACD_SIGNAL"]])
