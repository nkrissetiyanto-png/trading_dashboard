import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


# ======================================================
# NORMALIZER (wajib untuk crypto & saham indo)
# ======================================================
def normalize_df(df):
    rename_map = {}
    lower = {c.lower(): c for c in df.columns}

    if "close" in lower:
        rename_map[lower["close"]] = "Close"
    if "open" in lower:
        rename_map[lower["open"]] = "Open"
    if "high" in lower:
        rename_map[lower["high"]] = "High"
    if "low" in lower:
        rename_map[lower["low"]] = "Low"
    if "volume" in lower:
        rename_map[lower["volume"]] = "Volume"

    df = df.rename(columns=rename_map)
    return df


# ======================================================
# INDICATOR CALCULATIONS
# ======================================================
def EMA(series, period):
    return series.ewm(span=period, adjust=False).mean()

def RSI(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(span=period).mean()
    loss = (-delta.clip(upper=0)).ewm(span=period).mean()
    RS = gain / loss
    return 100 - (100 / (1 + RS))

def MACD(series):
    exp1 = EMA(series, 12)
    exp2 = EMA(series, 26)
    macd = exp1 - exp2
    signal = EMA(macd, 9)
    return macd, signal

def Bollinger(series, period=20, std=2):
    mid = series.rolling(period).mean()
    sd = series.rolling(period).std()
    upper = mid + std * sd
    lower = mid - std * sd
    return mid, upper, lower

def ATR(df, period=14):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)

    return tr.rolling(period).mean()

def Supertrend(df, period=10, multiplier=3):
    atr = ATR(df, period)
    hl2 = (df["High"] + df["Low"]) / 2

    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    st = pd.Series(index=df.index)
    direction = pd.Series(index=df.index)

    for i in range(1, len(df)):
        # Trend direction
        if df["Close"].iloc[i] > upperband.iloc[i - 1]:
            direction.iloc[i] = 1
        elif df["Close"].iloc[i] < lowerband.iloc[i - 1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i - 1]

        # Final supertrend band
        if direction.iloc[i] == 1:
            st.iloc[i] = lowerband.iloc[i]
        else:
            st.iloc[i] = upperband.iloc[i]

    return st, direction


# ======================================================
# RENDER PREMIUM MULTI-PANEL CHART
# ======================================================
def render_indicators(df):
    st.subheader("📊 Indicators Premium Level-4 (Pro Dashboard)")

    df = normalize_df(df).copy()

    # ===========================
    # CALCULATE INDICATORS
    # ===========================
    df["EMA20"] = EMA(df["Close"], 20)
    df["RSI"] = RSI(df["Close"])
    df["MACD"], df["MACD_SIGNAL"] = MACD(df["Close"])
    df["BB_MID"], df["BB_UP"], df["BB_LOW"] = Bollinger(df["Close"])
    df["ATR"] = ATR(df)
    df["VOL_EMA"] = EMA(df["Volume"], 20)
    df["ST"], df["ST_DIR"] = Supertrend(df)

    # ===========================
    # FIGURE
    # ===========================
    fig = go.Figure()

    # -------------------------------------------------
    # PANEL 1 — PRICE + EMA + BB + SUPERTREND
    # -------------------------------------------------
    # Price
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"],
        mode="lines", name="Close",
        line=dict(color="#60a5fa", width=1.8)
    ))

    # EMA20
    fig.add_trace(go.Scatter(
        x=df.index, y=df["EMA20"],
        mode="lines", name="EMA20",
        line=dict(color="#f59e0b", width=1.5)
    ))

    # Bollinger Bands
    fig.add_trace(go.Scatter(
        x=df.index, y=df["BB_UP"],
        line=dict(color="rgba(255,255,255,0.25)", width=1),
        name="BB Upper",
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["BB_LOW"],
        line=dict(color="rgba(255,255,255,0.25)", width=1),
        name="BB Lower",
        fill="tonexty",
        fillcolor="rgba(255,255,255,0.05)"
    ))

    # Supertrend
    fig.add_trace(go.Scatter(
        x=df.index, y=df["ST"],
        mode="lines",
        name="Supertrend",
        line=dict(
            color=df["ST_DIR"].apply(lambda x: "#22c55e" if x==1 else "#ef4444"),
            width=2
        )
    ))

    # -------------------------------------------------
    # PANEL 2 — VOLUME + VOL EMA
    # -------------------------------------------------
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"],
        name="Volume",
        marker_color="rgba(96,165,250,0.35)",
        yaxis="y2"
    ))

    fig.add_trace(go.Scatter(
        x=df.index, y=df["VOL_EMA"],
        mode="lines",
        name="Volume EMA",
        line=dict(color="#f97316", width=1.8),
        yaxis="y2"
    ))

    # -------------------------------------------------
    # PANEL 3 — RSI
    # -------------------------------------------------
    fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"],
        mode="lines",
        name="RSI",
        line=dict(color="#34d399", width=1.4),
        yaxis="y3"
    ))

    fig.add_hline(y=70, line_color="rgba(255,0,0,0.4)", yref="y3")
    fig.add_hline(y=30, line_color="rgba(0,255,0,0.4)", yref="y3")

    # -------------------------------------------------
    # PANEL 4 — MACD
    # -------------------------------------------------
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD"],
        mode="lines",
        name="MACD",
        line=dict(color="#a78bfa", width=1.5),
        yaxis="y4"
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD_SIGNAL"],
        mode="lines",
        name="Signal",
        line=dict(color="#fbcfe8", width=1.5),
        yaxis="y4"
    ))

    # ===========================
    # LAYOUT
    # ===========================
    fig.update_layout(
        height=1100,
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font=dict(color="#e2e8f0"),

        xaxis=dict(domain=[0, 1], showgrid=False),

        # PANEL DOMAINS
        yaxis=dict(  # PRICE
            domain=[0.58, 1.00],
            title="Price",
            gridcolor="rgba(255,255,255,0.05)"
        ),
        yaxis2=dict(  # VOLUME
            domain=[0.43, 0.56],
            title="Volume",
            gridcolor="rgba(255,255,255,0.05)"
        ),
        yaxis3=dict(  # RSI
            domain=[0.22, 0.40],
            title="RSI",
            gridcolor="rgba(255,255,255,0.05)",
            range=[0, 100]
        ),
        yaxis4=dict(  # MACD
            domain=[0.05, 0.20],
            title="MACD",
            gridcolor="rgba(255,255,255,0.05)"
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),

        margin=dict(l=40, r=40, t=80, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)
