import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ======================================================
# INDICATOR FUNCTIONS
# ======================================================

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

def MACD(series):
    ema12 = EMA(series, 12)
    ema26 = EMA(series, 26)
    macd = ema12 - ema26
    signal = EMA(macd, 9)
    hist = macd - signal
    return macd, signal, hist

def Bollinger(series, period=20, dev=2):
    ma = series.rolling(period).mean()
    std = series.rolling(period).std()
    upper = ma + dev * std
    lower = ma - dev * std
    return upper, ma, lower

# ======================================================
# MAIN RENDER
# ======================================================

def render_indicators(df: pd.DataFrame):
    st.subheader("📊 Technical Indicators (Premium • Clean Mode)")

    df = df.copy()

    # === SAFETY CHECK ===
    required_cols = {"open", "high", "low", "close"}
    if not required_cols.issubset(df.columns):
        st.error("Data tidak lengkap untuk indikator.")
        return

    # === CALCULATIONS ===
    df["EMA20"] = EMA(df["close"], 20)
    df["EMA50"] = EMA(df["close"], 50)
    df["EMA100"] = EMA(df["close"], 100)
    df["EMA200"] = EMA(df["close"], 200)

    df["BB_UP"], df["BB_MID"], df["BB_LOW"] = Bollinger(df["close"])

    df["RSI"] = RSI(df["close"])
    df["MACD"], df["MACD_SIGNAL"], df["MACD_HIST"] = MACD(df["close"])

    # ======================================================
    # FIGURE (2 PANELS ONLY)
    # ======================================================

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.7, 0.3],
        subplot_titles=("Price & Trend", "Momentum (RSI + MACD)")
    )

    # =====================
    # PANEL 1 — PRICE
    # =====================

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Price",
        increasing_line_color="#2ecc71",
        decreasing_line_color="#e74c3c"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], name="EMA20", line=dict(color="gold", width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"], name="EMA50", line=dict(color="#3498db", width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA100"], name="EMA100", line=dict(color="#9b59b6", width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA200"], name="EMA200", line=dict(color="#e74c3c", width=1)), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["BB_UP"],
        name="BB Upper",
        line=dict(color="rgba(155,89,182,0.4)", dash="dot")
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["BB_LOW"],
        name="BB Lower",
        line=dict(color="rgba(155,89,182,0.4)", dash="dot")
    ), row=1, col=1)

    # =====================
    # PANEL 2 — MOMENTUM
    # =====================

    fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"],
        name="RSI",
        line=dict(color="#1abc9c", width=1.5)
    ), row=2, col=1)

    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color="gray", row=2, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD"],
        name="MACD",
        line=dict(color="#3498db", width=1)
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD_SIGNAL"],
        name="Signal",
        line=dict(color="orange", width=1)
    ), row=2, col=1)

    fig.add_trace(go.Bar(
        x=df.index, y=df["MACD_HIST"],
        name="Histogram",
        marker_color="rgba(255,255,255,0.25)"
    ), row=2, col=1)

    # =====================
    # LAYOUT
    # =====================

    fig.update_layout(
        template="plotly_dark",
        height=720,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=11)
        ),
        xaxis_rangeslider_visible=False
    )

    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Momentum", row=2, col=1, range=[-100, 100])

    st.plotly_chart(fig, use_container_width=True)
