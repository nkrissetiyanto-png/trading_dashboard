import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ----------------------------- #
#      Indicator Functions      #
# ----------------------------- #

def EMA(series, period):
    return series.ewm(span=period, adjust=False).mean()

def RSI(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).ewm(span=period).mean()
    loss = -delta.where(delta < 0, 0).ewm(span=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def MACD(series):
    exp1 = EMA(series, 12)
    exp2 = EMA(series, 26)
    macd = exp1 - exp2
    signal = EMA(macd, 9)
    hist = macd - signal
    return macd, signal, hist

def STC(series, cycle=10, fast=23, slow=50):
    macd = EMA(series, fast) - EMA(series, slow)
    stoch = (macd - macd.rolling(cycle).min()) / (macd.rolling(cycle).max() - macd.rolling(cycle).min())
    return stoch * 100


# ----------------------------- #
#     Core Renderer Function     #
# ----------------------------- #

def render_indicators(df):

    st.subheader("📊 Premium Technical Indicators (Level 6 — Institutional Gold)")

    # Ensure index is datetime
    df.index = pd.to_datetime(df.index)

    # Compute Indicators
    df["EMA20"] = EMA(df["close"], 20)
    df["EMA50"] = EMA(df["close"], 50)
    df["EMA200"] = EMA(df["close"], 200)

    df["RSI"] = RSI(df["close"])
    df["MACD"], df["MACD_SIGNAL"], df["MACD_HIST"] = MACD(df["close"])

    df["ST_K"] = STC(df["close"])
    df["ST_D"] = df["ST_K"].rolling(3).mean()

    df["BB_MID"] = df["close"].rolling(20).mean()
    df["BB_STD"] = df["close"].rolling(20).std()
    df["BB_UPPER"] = df["BB_MID"] + 2 * df["BB_STD"]
    df["BB_LOWER"] = df["BB_MID"] - 2 * df["BB_STD"]

    df["VOL_MA"] = df["volume"].rolling(20).mean()

    # Make Subplot Layout (5 panels)
    fig = make_subplots(
        rows=5,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.015,
        row_heights=[0.40, 0.14, 0.18, 0.14, 0.14],
    )

    # ----------------------------- #
    # 1️⃣ Price + EMA + Bollinger   #
    # ----------------------------- #

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        name="Price",
        increasing_line_color="#22c55e",
        decreasing_line_color="#ef4444",
        showlegend=True
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], name="EMA20 (Gold)",
                             line=dict(color="#f59e0b", width=1.8)), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"], name="EMA50 (Blue)",
                             line=dict(color="#3b82f6", width=1.5)), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["EMA200"], name="EMA200 (Red)",
                             line=dict(color="#ef4444", width=1.5)), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["BB_UPPER"], name="BB Upper",
                             line=dict(color="rgba(245,158,11,0.35)", width=1)), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["BB_LOWER"], name="BB Lower",
                             line=dict(color="rgba(245,158,11,0.35)", width=1)), row=1, col=1)

    # ----------------------------- #
    # 2️⃣ RSI                       #
    # ----------------------------- #

    fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"],
        name="RSI",
        line=dict(color="#c084fc", width=2)
    ), row=2, col=1)

    # RSI zones
    fig.add_hline(y=70, line=dict(color="#ef4444", width=1, dash="dot"), row=2, col=1)
    fig.add_hline(y=30, line=dict(color="#22c55e", width=1, dash="dot"), row=2, col=1)

    # ----------------------------- #
    # 3️⃣ MACD                      #
    # ----------------------------- #

    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD"],
        name="MACD",
        line=dict(color="#22d3ee", width=2)
    ), row=3, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD_SIGNAL"],
        name="Signal",
        line=dict(color="#eab308", width=1.6)
    ), row=3, col=1)

    fig.add_trace(go.Bar(
        x=df.index, y=df["MACD_HIST"],
        name="Histogram",
        marker_color=np.where(df["MACD_HIST"] >= 0, "#22c55e", "#ef4444")
    ), row=3, col=1)

    # ----------------------------- #
    # 4️⃣ Stochastic                #
    # ----------------------------- #

    fig.add_trace(go.Scatter(
        x=df.index, y=df["ST_K"], name="ST %K",
        line=dict(color="#06b6d4", width=2)
    ), row=4, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["ST_D"], name="ST %D",
        line=dict(color="#ec4899", width=1.6)
    ), row=4, col=1)

    fig.add_hline(y=80, line=dict(color="#ef4444", width=1, dash="dot"), row=4, col=1)
    fig.add_hline(y=20, line=dict(color="#22c55e", width=1, dash="dot"), row=4, col=1)

    # ----------------------------- #
    # 5️⃣ Volume                    #
    # ----------------------------- #

    fig.add_trace(go.Bar(
        x=df.index,
        y=df["volume"],
        name="Volume",
        marker_color=np.where(df["close"] >= df["close"].shift(1), "#f59e0b", "#1f2937")
    ), row=5, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["VOL_MA"],
        name="VOL MA20",
        line=dict(color="#eab308", width=1.6)
    ), row=5, col=1)

    # ----------------------------- #
    # Layout Settings               #
    # ----------------------------- #

    fig.update_layout(
        template="plotly_dark",
        height=1200,
        showlegend=True,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0.15)",
            borderwidth=1,
            font=dict(size=11)
        ),
        margin=dict(l=40, r=40, t=40, b=20),
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
    )

    # Y-axis titles (optional)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1)
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_yaxes(title_text="Stochastic", row=4, col=1)
    fig.update_yaxes(title_text="Volume", row=5, col=1)

    # Render
    st.plotly_chart(fig, use_container_width=True)
