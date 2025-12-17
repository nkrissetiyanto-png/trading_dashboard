import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------------------------------------
#               UTILITY INDICATOR FUNCTIONS
# ---------------------------------------------------------

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
    hist = macd - signal
    return macd, signal, hist

def BollingerBands(series, period=20, mult=2):
    basis = series.rolling(period).mean()
    std = series.rolling(period).std()
    upper = basis + mult * std
    lower = basis - mult * std
    return upper, basis, lower

def StochasticOscillator(df, k_period=14, d_period=3):
    low_min = df["low"].rolling(k_period).min()
    high_max = df["high"].rolling(k_period).max()
    k = 100 * (df["close"] - low_min) / (high_max - low_min)
    d = k.rolling(d_period).mean()
    return k, d

def Supertrend(df, period=10, multiplier=3):
    hl2 = (df["high"] + df["low"]) / 2
    atr = df["high"].rolling(period).max() - df["low"].rolling(period).min()
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)

    st = pd.Series(index=df.index)
    direction = pd.Series(index=df.index)

    st.iloc[0] = hl2.iloc[0]
    direction.iloc[0] = 1

    for i in range(1, len(df)):
        curr_upper = upperband.iloc[i]
        prev_upper = upperband.iloc[i - 1]
        curr_lower = lowerband.iloc[i]
        prev_lower = lowerband.iloc[i - 1]
        prev_st = st.iloc[i - 1]

        if (curr_upper < prev_st) or (df["close"].iloc[i - 1] > prev_upper):
            upper = curr_upper
        else:
            upper = prev_upper

        if (curr_lower > prev_st) or (df["close"].iloc[i - 1] < prev_lower):
            lower = curr_lower
        else:
            lower = prev_lower

        if df["close"].iloc[i] <= upper:
            st.iloc[i] = upper
            direction.iloc[i] = -1
        else:
            st.iloc[i] = lower
            direction.iloc[i] = 1

    return st, direction

# ---------------------------------------------------------
#                  MAIN RENDER INDICATORS
# ---------------------------------------------------------

def render_indicators(df):

    st.subheader("📊 Premium Indicators (Auto-Fix Level 6)")

    # ----------------------------------------
    # DATA AUTO-FIX
    # ----------------------------------------
    df = df.copy()
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="last")]

    # Minimum candles to avoid distorted charts
    if len(df) < 50:
        st.warning("⚠️ Data terlalu sedikit. Minimal 50 candle untuk indikator premium.")
        st.dataframe(df)
        return

    df = df.ffill().bfill()

    # ----------------------------------------
    # CALCULATE INDICATORS
    # ----------------------------------------
    df["EMA20"] = EMA(df["close"], 20)
    df["EMA50"] = EMA(df["close"], 50)
    df["EMA100"] = EMA(df["close"], 100)
    df["EMA200"] = EMA(df["close"], 200)

    df["BB_Upper"], df["BB_Middle"], df["BB_Lower"] = BollingerBands(df["close"])
    df["RSI"] = RSI(df["close"])
    df["MACD"], df["MACD_Signal"], df["MACD_Hist"] = MACD(df["close"])
    df["ST_K"], df["ST_D"] = StochasticOscillator(df)

    df["ST_Value"], df["ST_Dir"] = Supertrend(df)

    df["VOL_MA20"] = df["volume"].rolling(20).mean()

    # ----------------------------------------
    # CREATE MULTI-PANEL LAYOUT
    # ----------------------------------------
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.45, 0.15, 0.20, 0.20],
        specs=[
            [{"type": "xy"}],
            [{"type": "xy"}],
            [{"type": "xy"}],
            [{"type": "xy"}]
        ]
    )

    # ----------------------------------------------------
    # 1️⃣ PRICE PANEL — Candles + EMA + Bollinger + ST
    # ----------------------------------------------------
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["open"], high=df["high"],
        low=df["low"], close=df["close"],
        name="Price",
        showlegend=True,
        increasing_line_color="#22c55e",
        decreasing_line_color="#ef4444",
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], mode="lines",
                             name="EMA20 (Gold)", line=dict(color="#fbbf24", width=1.8)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"], mode="lines",
                             name="EMA50 (Blue)", line=dict(color="#3b82f6", width=1.6)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA100"], mode="lines",
                             name="EMA100 (Red)", line=dict(color="#ef4444", width=1.3)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA200"], mode="lines",
                             name="EMA200 (Green)", line=dict(color="#22c55e", width=1.3)), row=1, col=1)

    # Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"], mode="lines",
                             name="BB Upper", line=dict(color="#a855f7", width=1, dash="dot")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"], mode="lines",
                             name="BB Lower", line=dict(color="#a855f7", width=1, dash="dot")), row=1, col=1)

    # Supertrend
    fig.add_trace(go.Scatter(x=df.index, y=df["ST_Value"],
                             mode="lines", name="Supertrend Up",
                             line=dict(color="#22c55e", width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["ST_Value"],
                             mode="lines", name="Supertrend Down",
                             line=dict(color="#ef4444", width=2)), row=1, col=1)

    # ----------------------------------------------------
    # 2️⃣ RSI PANEL
    # ----------------------------------------------------
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines",
                             name="RSI", line=dict(color="#10b981", width=2)), row=2, col=1)

    fig.add_hline(y=70, line=dict(color="#ef4444", width=1, dash="dot"), row=2, col=1)
    fig.add_hline(y=30, line=dict(color="#3b82f6", width=1, dash="dot"), row=2, col=1)

    # ----------------------------------------------------
    # 3️⃣ MACD PANEL
    # ----------------------------------------------------
    fig.add_trace(go.Bar(x=df.index, y=df["MACD_Hist"],
                         name="Histogram", marker_color="#a78bfa"), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"],
                             mode="lines", name="MACD", line=dict(color="#22c55e")), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD_Signal"],
                             mode="lines", name="Signal", line=dict(color="#ef4444")), row=3, col=1)

    # ----------------------------------------------------
    # 4️⃣ STOCHASTIC PANEL
    # ----------------------------------------------------
    fig.add_trace(go.Scatter(x=df.index, y=df["ST_K"],
                             mode="lines", name="%K", line=dict(color="#10b981")), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["ST_D"],
                             mode="lines", name="%D", line=dict(color="#fbbf24")), row=4, col=1)

    fig.add_hline(y=80, line=dict(color="#ef4444", width=1, dash="dot"), row=4, col=1)
    fig.add_hline(y=20, line=dict(color="#3b82f6", width=1, dash="dot"), row=4, col=1)

    # ----------------------------------------------------
    # STYLE
    # ----------------------------------------------------
    fig.update_layout(
        height=1200,
        template="plotly_dark",
        legend=dict(
            orientation="v",
            x=1.02,
            y=1,
            bgcolor="rgba(0,0,0,0.4)",
            bordercolor="rgba(255,255,255,0.15)"
        )
    )

    st.plotly_chart(fig, use_container_width=True)
