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
    loss = (-delta.where(delta < 0, 0)).ewm(span=period).mean()
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

    final_upper = upperband.copy()
    final_lower = lowerband.copy()

    for i in range(1, len(df)):
        if df["close"].iloc[i] > final_upper.iloc[i-1]:
            final_upper.iloc[i] = upperband.iloc[i]
        else:
            final_upper.iloc[i] = min(upperband.iloc[i], final_upper.iloc[i-1])

        if df["close"].iloc[i] < final_lower.iloc[i-1]:
            final_lower.iloc[i] = lowerband.iloc[i]
        else:
            final_lower.iloc[i] = max(lowerband.iloc[i], final_lower.iloc[i-1])

    trend = np.where(df["close"] > final_lower, 1, -1)

    return final_upper, final_lower, trend


# ============================================================
# LEVEL 5: Volume Heatmap + VWAP + Pressure Oscillator
# ============================================================

def calc_vwap(df):
    typical = (df["high"] + df["low"] + df["close"]) / 3
    vwap = (typical * df["volume"]).cumsum() / df["volume"].cumsum()
    return vwap


def calc_volume_heat(df):
    """
    Heat volume:
    - strong buy → bright green
    - strong sell → bright red
    - neutral → yellow/orange
    """
    df = df.copy()

    df["vol_norm"] = df["volume"] / df["volume"].rolling(20).mean()
    df["vol_norm"] = df["vol_norm"].clip(0.2, 3)

    return df["vol_norm"]


def calc_pressure(df):
    """
    Buy/Sell Pressure Oscillator (0–100)
    """
    buy = df["close"] - df["low"]
    sell = df["high"] - df["close"]

    pressure = buy / (buy + sell + 1e-9)
    pressure = pressure * 100
    pressure = pressure.rolling(5).mean()
    return pressure


# ============================================================
# RENDER (Ultra Premium)
# ============================================================

def render_indicators(df):

    st.subheader("📊 Premium Indicators Level 5 (Pro Pack)")

    # -------------------------------------
    # Compute all indicators
    # -------------------------------------
    df["EMA20"] = EMA(df["close"], 20)
    df["RSI"] = RSI(df["close"], 14)
    df["MACD"], df["MACD_SIGNAL"] = MACD(df["close"])
    df["ST_UP"], df["ST_DOWN"], df["ST_TREND"] = supertrend(df)
    df["VWAP"] = calc_vwap(df)
    df["VOL_HEAT"] = calc_volume_heat(df)
    df["PRESSURE"] = calc_pressure(df)

    # -------------------------------------
    # Create 4 Panels
    # -------------------------------------
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.50, 0.20, 0.20, 0.25],
        specs=[[{"type": "xy"}],
               [{"type": "xy"}],
               [{"type": "xy"}],
               [{"type": "xy"}]]
    )

    # ============================================================
    # PANEL 1 — Price, EMA20, SuperTrend
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
        name="SuperTrend Up"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["ST_DOWN"],
        mode="lines",
        line=dict(color="#EF5350", width=1),
        name="SuperTrend Down"
    ), row=1, col=1)

    # ============================================================
    # PANEL 2 — RSI
    # ============================================================

    fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"],
        mode="lines",
        line=dict(color="#00E5FF", width=1.8),
        name="RSI"
    ), row=2, col=1)

    fig.add_hline(y=70, line=dict(color="#EF5350", dash="dash"), row=2, col=1)
    fig.add_hline(y=30, line=dict(color="#66BB6A", dash="dash"), row=2, col=1)

    # ============================================================
    # PANEL 3 — MACD
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
    # PANEL 4 — Volume Heatmap + VWAP + Pressure
    # ============================================================

    # Volume heat (colored)
    fig.add_trace(go.Bar(
        x=df.index,
        y=df["volume"],
        marker=dict(
            color=df["VOL_HEAT"],
            colorscale=[[0, "#ff6b6b"], [0.5, "#FFD93D"], [1, "#4CAF50"]],
        ),
        name="Volume Heatmap",
        opacity=0.75
    ), row=4, col=1)

    # VWAP line
    fig.add_trace(go.Scatter(
        x=df.index, y=df["VWAP"],
        mode="lines",
        line=dict(color="#42A5F5", width=2),
        name="VWAP"
    ), row=4, col=1)

    # Pressure Oscillator
    fig.add_trace(go.Scatter(
        x=df.index, y=df["PRESSURE"],
        mode="lines",
        line=dict(color="#F06292", width=2),
        name="Buy/Sell Pressure"
    ), row=4, col=1)

    fig.add_hline(y=50, line=dict(color="#888", dash="dot"), row=4, col=1)

    # ============================================================
    # FINAL LAYOUT
    # ============================================================

    fig.update_layout(
        template="plotly_dark",
        height=1300,
        showlegend=True,
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(x=0, y=1.15, orientation="h")
    )

    st.plotly_chart(fig, use_container_width=True)
