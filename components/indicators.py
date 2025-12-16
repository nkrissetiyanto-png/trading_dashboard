import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =====================================================
# UTILITIES
# =====================================================

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

# ---------------------------
# SUPER TREND CALC
# ---------------------------

def calc_supertrend(df, period=10, multiplier=3):
    df = df.copy()

    df["TR"] = np.maximum.reduce([
        df["high"] - df["low"],
        (df["high"] - df["close"].shift()).abs(),
        (df["low"] - df["close"].shift()).abs()
    ])

    df["ATR"] = df["TR"].rolling(period).mean()

    hl2 = (df["high"] + df["low"]) / 2
    df["upperband"] = hl2 + multiplier * df["ATR"]
    df["lowerband"] = hl2 - multiplier * df["ATR"]

    df["ST"] = 0.0
    df["ST_DIR"] = 1

    for i in range(period, len(df)):
        prev = df["ST"].iloc[i - 1]

        # Determine direction
        if df["close"].iloc[i] > prev:
            df.at[i, "ST_DIR"] = 1
        else:
            df.at[i, "ST_DIR"] = -1

        # Pick band based on direction
        df.at[i, "ST"] = df["lowerband"].iloc[i] if df["ST_DIR"].iloc[i] == 1 else df["upperband"].iloc[i]

    return df


# ---------------------------
# TREND RIBBON (EMA HEATMAP)
# ---------------------------

def trend_ribbon(df):
    df = df.copy()
    ribbons = {
        "EMA20": EMA(df["close"], 20),
        "EMA50": EMA(df["close"], 50),
        "EMA100": EMA(df["close"], 100),
        "EMA200": EMA(df["close"], 200),
    }
    return ribbons


# =====================================================
# RENDER PREMIUM INDICATORS
# =====================================================

def render_indicators(df):
    st.subheader("📊 Premium Indicators (Unified Chart)")

    df = df.copy()

    # =================
    # CALCULATE ALL
    # =================
    df["EMA20"] = EMA(df["close"], 20)
    df["RSI"] = RSI(df["close"])
    df["MACD"], df["MACD_SIGNAL"] = MACD(df["close"])

    df = calc_supertrend(df)
    ribbons = trend_ribbon(df)

    # =====================================================
    # PLOTLY FIGURE
    # =====================================================

    fig = go.Figure()

    # -------------------------
    # PRICE (main)
    # -------------------------
    fig.add_trace(go.Scatter(
        x=df.index, y=df["close"],
        mode="lines",
        name="Close",
        line=dict(color="#38bdf8", width=2)
    ))

    # -------------------------
    # EMA20
    # -------------------------
    fig.add_trace(go.Scatter(
        x=df.index, y=df["EMA20"],
        mode="lines",
        name="EMA20",
        line=dict(color="#a855f7", width=1.5)
    ))

    # -------------------------
    # SUPER TREND FIXED (2 trace)
    # -------------------------

    # Bullish line (green)
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["ST"].where(df["ST_DIR"] == 1),
        mode="lines",
        name="Supertrend Up",
        line=dict(color="#22c55e", width=2)
    ))

    # Bearish line (red)
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["ST"].where(df["ST_DIR"] == -1),
        mode="lines",
        name="Supertrend Down",
        line=dict(color="#ef4444", width=2)
    ))

    # -------------------------
    # TREND RIBBON HEATMAP
    # -------------------------
    for name, series in ribbons.items():
        fig.add_trace(go.Scatter(
            x=df.index,
            y=series,
            mode="lines",
            name=name,
            line=dict(width=1),
            opacity=0.35
        ))

    # =====================================================
    # LAYOUT STYLING
    # =====================================================

    fig.update_layout(
        template="plotly_dark",
        height=650,
        margin=dict(l=40, r=40, t=40, b=40),
        showlegend=True,
        plot_bgcolor="rgba(17, 24, 39, 0.9)",
        paper_bgcolor="rgba(17, 24, 39, 0.0)",
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
    )

    # Y-axis formatting
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.1)")
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.1)")

    # =====================================================
    # RENDER
    # =====================================================
    st.plotly_chart(fig, use_container_width=True)
