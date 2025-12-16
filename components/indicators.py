import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ============================================================
# Technical Indicators
# ============================================================

def EMA(series, period):
    return series.ewm(span=period, adjust=False).mean()

def RSI(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).ewm(span=period).mean()
    loss = -delta.where(delta < 0, 0).ewm(span=period).mean()
    RS = gain / loss
    return 100 - (100 / (1 + RS))

def MACD(series):
    fast = EMA(series, 12)
    slow = EMA(series, 26)
    macd = fast - slow
    signal = EMA(macd, 9)
    return macd, signal

def supertrend(df, period=10, multiplier=3):
    hl2 = (df["high"] + df["low"]) / 2
    atr = df["high"].rolling(period).max() - df["low"].rolling(period).min()
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    final_upperband = upperband.copy()
    final_lowerband = lowerband.copy()

    for i in range(1, len(df)):
        if df["close"].iloc[i] > final_upperband.iloc[i-1]:
            final_upperband.iloc[i] = upperband.iloc[i]
        else:
            final_upperband.iloc[i] = min(upperband.iloc[i], final_upperband.iloc[i-1])

        if df["close"].iloc[i] < final_lowerband.iloc[i-1]:
            final_lowerband.iloc[i] = lowerband.iloc[i]
        else:
            final_lowerband.iloc[i] = max(lowerband.iloc[i], final_lowerband.iloc[i-1])

    trend = np.where(df["close"] > final_lowerband, 1, -1)
    return final_upperband, final_lowerband, trend


# ============================================================
# Rendering (Premium MT4 Style)
# ============================================================

def render_indicators(df):

    st.subheader("📊 Premium Indicators (Unified MT4 Style)")

    # -------------------------------------
    # Compute Indicators
    # -------------------------------------
    df["EMA20"] = EMA(df["close"], 20)
    df["RSI"] = RSI(df["close"], 14)
    df["MACD"], df["MACD_SIGNAL"] = MACD(df["close"])
    df["ST_UP"], df["ST_DOWN"], df["ST_TREND"] = supertrend(df)

    # -------------------------------------
    # Create Subplots (3-panel)
    # -------------------------------------
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.55, 0.25, 0.20],
        specs=[[{"type": "xy"}],
               [{"type": "xy"}],
               [{"type": "xy"}]]
    )

    # ============================================================
    # Panel 1 — Price + EMA20 + SuperTrend
    # ============================================================

    fig.add_trace(go.Scatter(
        x=df.index, y=df["close"],
        mode="lines",
        line=dict(color="#4FC3F7", width=2),
        name="Close"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["EMA20"],
        mode="lines",
        line=dict(color="#E57373", width=1.8),
        name="EMA20"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["ST_UP"],
        mode="lines",
        line=dict(color="#66BB6A", width=1),
        name="Supertrend Up"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["ST_DOWN"],
        mode="lines",
        line=dict(color="#EF5350", width=1),
        name="Supertrend Down"
    ), row=1, col=1)


    # ============================================================
    # Panel 2 — RSI
    # ============================================================

    fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"],
        mode="lines",
        line=dict(color="#00E5FF", width=1.8),
        name="RSI"
    ), row=2, col=1)

    # Overbought 70
    fig.add_hline(y=70, line=dict(color="#EF5350", width=1, dash="dash"),
                  row=2, col=1)

    # Oversold 30
    fig.add_hline(y=30, line=dict(color="#66BB6A", width=1, dash="dash"),
                  row=2, col=1)


    # ============================================================
    # Panel 3 — MACD
    # ============================================================

    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD"],
        mode="lines",
        line=dict(color="#FFB74D", width=1.8),
        name="MACD"
    ), row=3, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD_SIGNAL"],
        mode="lines",
        line=dict(color="#BA68C8", width=1.5),
        name="Signal"
    ), row=3, col=1)


    # ============================================================
    # Final Layout
    # ============================================================

    fig.update_layout(
        template="plotly_dark",
        height=1000,
        showlegend=True,
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(x=0, y=1.12, orientation="h")
    )

    st.plotly_chart(fig, use_container_width=True)
