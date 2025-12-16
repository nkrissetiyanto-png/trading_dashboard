import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================
#     INDICATOR FUNCTIONS
# ==========================

def EMA(series, period):
    return series.ewm(span=period, adjust=False).mean()

def RSI(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).ewm(span=period).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(span=period).mean()
    RS = gain / loss
    return 100 - (100 / (1 + RS))

def MACD(series):
    exp1 = EMA(series, 12)
    exp2 = EMA(series, 26)
    macd = exp1 - exp2
    signal = EMA(macd, 9)
    return macd, signal

def Supertrend(df, atr_multiplier=3, atr_period=10):
    high = df["high"]
    low = df["low"]
    close = df["close"]

    # ATR
    hl = high - low
    hc = (high - close.shift()).abs()
    lc = (low - close.shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    atr = tr.rolling(atr_period).mean()

    # basic bands
    upper_basic = (high + low) / 2 + atr_multiplier * atr
    lower_basic = (high + low) / 2 - atr_multiplier * atr

    upper = upper_basic.copy()
    lower = lower_basic.copy()

    for i in range(1, len(df)):
        upper[i] = upper_basic[i] if (
            upper_basic[i] < upper[i - 1] or close[i - 1] > upper[i - 1]
        ) else upper[i - 1]

        lower[i] = lower_basic[i] if (
            lower_basic[i] > lower[i - 1] or close[i - 1] < lower[i - 1]
        ) else lower[i - 1]

    st_trend = np.where(close > upper, lower, upper)
    return st_trend


# ==========================
#       RENDER CHART
# ==========================

def render_indicators(df):

    st.subheader("📊 Premium Technical Indicators (Level 6)")

    # ==============================
    # Calculate Indicators
    # ==============================
    df["EMA20"] = EMA(df["close"], 20)
    df["RSI"] = RSI(df["close"])
    df["MACD"], df["MACD_SIGNAL"] = MACD(df["close"])
    df["ST"] = Supertrend(df)

    # Trend strength ribbon (0–100)
    df["RIBBON"] = (
        (df["EMA20"].diff() > 0).astype(int) * 40 +
        (df["MACD"] > df["MACD_SIGNAL"]).astype(int) * 30 +
        (df["close"] > df["EMA20"]).astype(int) * 30
    )

    # ==============================
    # MAIN PLOT LAYOUT
    # ==============================
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.55, 0.25, 0.20],
        vertical_spacing=0.02
    )

    # ==============================
    # 1 — PRICE + EMA20 + SUPERTREND
    # ==============================
    fig.add_trace(go.Scatter(
        x=df.index, y=df["close"],
        name="Close",
        line=dict(color="#00E5FF", width=2)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["EMA20"],
        name="EMA 20",
        line=dict(color="#FFD54F", width=1.5)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["ST"],
        name="Supertrend",
        line=dict(color="#66FF99", width=1.2, dash="dot")
    ), row=1, col=1)

    # ==============================
    # Trend Ribbon (STATIC FILL)
    # ==============================
    trend_color = (
        "rgba(76,175,80,0.20)" if df["RIBBON"].iloc[-1] > 70 else
        "rgba(255,235,59,0.20)" if df["RIBBON"].iloc[-1] > 40 else
        "rgba(244,67,54,0.20)"
    )

    fig.add_trace(go.Scatter(
        x=df.index, y=df["close"],
        fill="tozeroy",
        fillcolor=trend_color,
        line=dict(width=0),
        name="Trend Zone",
        hoverinfo="skip",
        showlegend=False
    ), row=1, col=1)

    # ==============================
    # 2 — RSI PANEL
    # ==============================
    fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"],
        name="RSI",
        line=dict(color="#42A5F5", width=1.8),
    ), row=2, col=1)

    # RSI zones
    fig.add_hrect(
        y0=70, y1=100,
        fillcolor="rgba(255,82,82,0.15)", line_width=0, row=2, col=1
    )
    fig.add_hrect(
        y0=0, y1=30,
        fillcolor="rgba(0,230,118,0.15)", line_width=0, row=2, col=1
    )

    # ==============================
    # 3 — MACD PANEL
    # ==============================
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD"],
        name="MACD",
        line=dict(color="#FFAB40", width=1.5)
    ), row=3, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD_SIGNAL"],
        name="Signal",
        line=dict(color="#Bdbdbd", width=1)
    ), row=3, col=1)

    fig.add_hline(y=0, line_width=1, line_color="gray", row=3, col=1)

    # ==============================
    # FINAL LAYOUT
    # ==============================
    fig.update_layout(
        height=820,
        template="plotly_dark",
        margin=dict(l=25, r=25, t=40, b=20),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
