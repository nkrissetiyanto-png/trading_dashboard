import streamlit as st
import pandas as pd

def rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def render_indicators(df):
    st.subheader("📊 Indicators")

    df['EMA_20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['RSI'] = rsi(df['close'])

    st.line_chart(df[['close', 'EMA_20']])
    st.line_chart(df[['RSI']])
