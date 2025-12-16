import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


# ===========================
# Indicator Functions
# ===========================

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


# ===========================
# MAIN RENDER FUNCTION
# ===========================

def render_indicators(df):
    st.subheader("📊 Technical Indicators Premium")

    df["EMA20"] = EMA(df["close"], 20)
    df["RSI"] = RSI(df["close"])
    df["MACD"], df["MACD_SIGNAL"] = MACD(df["close"])

    # ===============================
    # MULTI-PANEL → SINGLE CHART
    # ===============================
    fig = go.Figure()

    # ---------------------------
    # Panel 1: Price + EMA20
    # ---------------------------
    fig.add_trace(go.Scatter(
        x=df.index, y=df["close"],
        mode="lines",
        name="Close",
        line=dict(width=1.8, color="#60a5fa")
    ))

    fig.add_trace(go.Scatter(
        x=df.index, y=df["EMA20"],
        mode="lines",
        name="EMA20",
        line=dict(width=1.5, color="#f97316")
    ))

    # ---------------------------
    # Panel 2: RSI
    # ---------------------------
    fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"],
        mode="lines",
        name="RSI",
        line=dict(width=1.4, color="#34d399"),
        yaxis="y2"
    ))

    # RSI thresholds
    fig.add_hline(y=70, line_dash="dash", line_color="rgba(255,0,0,0.4)", yref="y2")
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(0,255,0,0.4)", yref="y2")

    # ---------------------------
    # Panel 3: MACD
    # ---------------------------
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD"],
        mode="lines",
        name="MACD",
        line=dict(width=1.4, color="#a78bfa"),
        yaxis="y3"
    ))

    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD_SIGNAL"],
        mode="lines",
        name="Signal",
        line=dict(width=1.4, color="#fbcfe8"),
        yaxis="y3"
    ))

    # ===============================
    # LAYOUT — 3 PANELS IN 1 CHART
    # ===============================
    fig.update_layout(

        # MANUAL DARK MODE → TANPA TEMPLATE
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font=dict(color="#e2e8f0"),

        # 3 Y AXES
        xaxis=dict(
            domain=[0, 1],
            showgrid=False
        ),

        yaxis=dict(             # Panel 1 (Price)
            domain=[0.60, 1.00],
            title="Price",
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)"
        ),

        yaxis2=dict(            # Panel 2 (RSI)
            domain=[0.33, 0.58],
            title="RSI",
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            range=[0, 100]
        ),

        yaxis3=dict(            # Panel 3 (MACD)
            domain=[0.05, 0.30],
            title="MACD",
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)"
        ),

        height=900,
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
