import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ============================================================
# BASIC INDICATORS
# ============================================================

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


# ============================================================
# SUPERTREND
# ============================================================

def supertrend(df, period=10, multiplier=3):
    hl2 = (df["high"] + df["low"]) / 2
    tr = np.maximum(df["high"] - df["low"],
                    np.maximum(abs(df["high"] - df["close"].shift()),
                               abs(df["low"] - df["close"].shift())))
    atr = tr.rolling(period).mean()

    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    trend = [1]
    st = [upperband.iloc[0]]

    for i in range(1, len(df)):
        if df["close"].iloc[i] > upperband.iloc[i-1]:
            trend.append(1)
            st.append(lowerband.iloc[i])
        elif df["close"].iloc[i] < lowerband.iloc[i-1]:
            trend.append(-1)
            st.append(upperband.iloc[i])
        else:
            trend.append(trend[-1])
            st.append(st[-1])

    df["ST"] = st
    df["ST_TREND"] = trend
    df["ST_UP"] = np.where(df["ST_TREND"] == 1, df["ST"], np.nan)
    df["ST_DOWN"] = np.where(df["ST_TREND"] == -1, df["ST"], np.nan)
    return df


# ============================================================
# LEVEL 6 – TREND RIBBON
# ============================================================

def trend_ribbon(df):
    ema10 = EMA(df["close"], 10)
    ema20 = EMA(df["close"], 20)
    ema50 = EMA(df["close"], 50)
    ema100 = EMA(df["close"], 100)

    score = (
        (ema10 > ema20).astype(int) +
        (ema20 > ema50).astype(int) +
        (ema50 > ema100).astype(int)
    )

    return (score / 3) * 100  # 0–100


# ============================================================
# LEVEL 6 – ATR VOLATILITY CLOUD
# ============================================================

def atr_cloud(df, period=14, multiplier=1.5):
    tr = np.maximum(df["high"] - df["low"],
                    np.maximum(abs(df["high"] - df["close"].shift()),
                               abs(df["low"] - df["close"].shift())))
    atr = tr.rolling(period).mean()

    top = df["close"] + atr * multiplier
    bot = df["close"] - atr * multiplier
    return top, bot


# ============================================================
# LEVEL 6 – LIQUIDITY ZONES (SUPPLY/DEMAND)
# ============================================================

def find_liquidity_zones(df, lookback=12):
    demand = []
    supply = []

    for i in range(lookback, len(df) - lookback):
        low_pvt = df["low"].iloc[i] == df["low"].iloc[i-lookback:i+lookback].min()
        high_pvt = df["high"].iloc[i] == df["high"].iloc[i-lookback:i+lookback].max()

        if low_pvt:
            demand.append((df.index[i], df["low"].iloc[i]))
        if high_pvt:
            supply.append((df.index[i], df["high"].iloc[i]))

    return demand, supply


# ============================================================
# LEVEL 6 – ALGO BIAS SCORE
# ============================================================

def algo_bias(df):
    score = 0

    # EMA stack (40%)
    ema10 = EMA(df["close"], 10)
    ema20 = EMA(df["close"], 20)
    ema50 = EMA(df["close"], 50)
    ema_score = (
        (ema10 > ema20).astype(int) +
        (ema20 > ema50).astype(int)
    ) / 2 * 40

    # Supertrend (30%)
    st_bias = np.where(df["ST_TREND"] == 1, 30, 0)

    # MACD histogram (20%)
    hist = df["MACD"] - df["MACD_SIGNAL"]
    macd_bias = np.where(hist > 0, 20, 0)

    # ATR volatility regime (10%)
    tr = np.maximum(df["high"] - df["low"],
                    np.maximum(abs(df["high"] - df["close"].shift()),
                               abs(df["low"] - df["close"].shift())))
    atr = tr.rolling(14).mean()
    atr_bias = (atr / atr.max() * 10)

    score = ema_score + st_bias + macd_bias + atr_bias
    return score.clip(0, 100)


# ============================================================
# RENDER PREMIUM LEVEL 6
# ============================================================

def render_indicators(df):
    st.subheader("📈 Premium Indicators (Unified Multi-Panel – Level 6)")

    # --------------------------
    # Calculate all indicators
    # --------------------------
    df = df.copy()

    df["EMA20"] = EMA(df["close"], 20)
    df["EMA50"] = EMA(df["close"], 50)
    df["EMA100"] = EMA(df["close"], 100)
    df["EMA200"] = EMA(df["close"], 200)

    df["RSI"] = RSI(df["close"])
    df["MACD"], df["MACD_SIGNAL"] = MACD(df["close"])

    df = supertrend(df)

    df["RIBBON"] = trend_ribbon(df)
    df["CLOUD_TOP"], df["CLOUD_BOT"] = atr_cloud(df)
    df["ALGO_BIAS"] = algo_bias(df)
    demand, supply = find_liquidity_zones(df)

    # ============================================================
    # BUILD 5-PANEL FIGURE
    # ============================================================

    fig = make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.50, 0.20, 0.20, 0.25, 0.20],
        specs=[[{"type": "xy"}],
               [{"type": "xy"}],
               [{"type": "xy"}],
               [{"type": "xy"}],
               [{"type": "xy"}]]
    )

    # ------------------------------------------------------------
    # PANEL 1 – PRICE + EMA + SUPER TREND + RIBBON + CLOUD + ZONES
    # ------------------------------------------------------------

    # Trend Ribbon background
    fig.add_trace(go.Scatter(
        x=df.index, y=df["close"],
        fill="tozeroy",
        fillcolor=df["RIBBON"].apply(lambda v:
            "rgba(76,175,80,0.35)" if v > 70 else
            "rgba(255,235,59,0.35)" if v > 40 else
            "rgba(244,67,54,0.35)"
        ),
        line=dict(width=0),
        hoverinfo="skip",
        showlegend=False
    ), row=1, col=1)

    # ATR Cloud
    fig.add_trace(go.Scatter(
        x=df.index, y=df["CLOUD_TOP"],
        line=dict(width=0),
        showlegend=False
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["CLOUD_BOT"],
        fill="tonexty",
        fillcolor="rgba(33,150,243,0.15)",
        line=dict(width=0),
        name="Volatility Cloud"
    ), row=1, col=1)

    # Price
    fig.add_trace(go.Scatter(
        x=df.index, y=df["close"],
        name="Close",
        line=dict(color="#00BFFF", width=2)
    ), row=1, col=1)

    # EMA stack
    for (col, color) in [
        ("EMA20", "#9C27B0"),
        ("EMA50", "#F57C00"),
        ("EMA100", "#FFC107"),
        ("EMA200", "#8BC34A"),
    ]:
        fig.add_trace(go.Scatter(
            x=df.index, y=df[col],
            name=col,
            line=dict(color=color, width=1.5)
        ), row=1, col=1)

    # Supertrend
    fig.add_trace(go.Scatter(
        x=df.index, y=df["ST_UP"],
        name="Supertrend Up",
        line=dict(color="#4CAF50", width=2)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["ST_DOWN"],
        name="Supertrend Down",
        line=dict(color="#FF5252", width=2)
    ), row=1, col=1)

    # Liquidity zones
    for t, price in demand:
        fig.add_vrect(
            x0=t, x1=t,
            y0=price, y1=price * 1.015,
            fillcolor="green", opacity=0.25, line_width=0
        )

    for t, price in supply:
        fig.add_vrect(
            x0=t, x1=t,
            y0=price, y1=price * 0.985,
            fillcolor="red", opacity=0.25, line_width=0
        )

    # ------------------------------------------------------------
    # PANEL 2 – RSI
    # ------------------------------------------------------------

    fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"],
        name="RSI",
        line=dict(color="#00E676", width=2)
    ), row=2, col=1)

    fig.add_hline(y=70, line=dict(color="red", dash="dot"), row=2, col=1)
    fig.add_hline(y=30, line=dict(color="green", dash="dot"), row=2, col=1)

    # ------------------------------------------------------------
    # PANEL 3 – MACD
    # ------------------------------------------------------------

    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD"],
        name="MACD",
        line=dict(color="#FFEB3B", width=2)
    ), row=3, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD_SIGNAL"],
        name="Signal",
        line=dict(color="#FF9800", width=1.5)
    ), row=3, col=1)

    # ------------------------------------------------------------
    # PANEL 4 – Supertrend Value
    # ------------------------------------------------------------

    fig.add_trace(go.Scatter(
        x=df.index, y=df["ST"],
        name="Supertrend Value",
        line=dict(color="#90CAF9", width=2)
    ), row=4, col=1)

    # ------------------------------------------------------------
    # PANEL 5 – Algo Bias Score
    # ------------------------------------------------------------

    fig.add_trace(go.Scatter(
        x=df.index, y=df["ALGO_BIAS"],
        name="Algo Bias Score",
        line=dict(color="#FFEB3B", width=2)
    ), row=5, col=1)

    fig.add_hline(y=70, line=dict(color="#66BB6A", dash="dot"), row=5, col=1)
    fig.add_hline(y=30, line=dict(color="#EF5350", dash="dot"), row=5, col=1)

    # ------------------------------------------------------------
    # LAYOUT CONFIG
    # ------------------------------------------------------------

    fig.update_layout(
        height=1600,
        template="plotly_dark",
        showlegend=True,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0.4)")
    )

    st.plotly_chart(fig, use_container_width=True)
