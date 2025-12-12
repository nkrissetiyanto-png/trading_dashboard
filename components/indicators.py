import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


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


def render_indicators(df):
    st.subheader("📊 Technical Indicators Premium")

    # --- Calculate indicators ---
    df["EMA20"] = EMA(df["close"], 20)
    df["RSI"] = RSI(df["close"])
    df["MACD"], df["MACD_SIGNAL"] = MACD(df["close"])

    # --- Create multi-panel figure ---
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.5, 0.25, 0.25],
        vertical_spacing=0.03
    )

    # --- Chart 1: Price + EMA ---
    fig.add_trace(
        go.Scatter(x=df.index, y=df["close"], name="Close", mode="lines", line=dict(width=1.7)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["EMA20"], name="EMA20", mode="lines", line=dict(width=1.3)),
        row=1, col=1
    )

    # --- Chart 2: RSI ---
    fig.add_trace(
        go.Scatter(x=df.index, y=df["RSI"], name="RSI", mode="lines", line=dict(width=1.5)),
        row=2, col=1
    )
    fig.add_hline(y=70, line=dict(color="red", width=1, dash="dash"), row=2, col=1)
    fig.add_hline(y=30, line=dict(color="green", width=1, dash="dash"), row=2, col=1)

    # --- Chart 3: MACD ---
    fig.add_trace(
        go.Scatter(x=df.index, y=df["MACD"], name="MACD", mode="lines", line=dict(width=1.5)),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["MACD_SIGNAL"], name="Signal", mode="lines", line=dict(width=1.5)),
        row=3, col=1
    )

    # --- Layout ---
    fig.update_layout(
        height=900,
        showlegend=True,
        margin=dict(l=10, r=10, t=10, b=10),
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)
