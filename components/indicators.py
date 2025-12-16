import streamlit as st
import plotly.graph_objects as go

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

def render_indicators_premium_level2(df):
    st.subheader("📈 Technical Indicators Premium (1 Chart)")

    df["EMA20"] = EMA(df["close"], 20)
    df["RSI"] = RSI(df["close"])
    df["MACD"], df["MACD_SIGNAL"] = MACD(df["close"])

    fig = go.Figure()

    # ===========================
    # 1) Close & EMA (Primary Axis)
    # ===========================
    fig.add_trace(go.Scatter(
        x=df.index, y=df["close"],
        mode="lines",
        name="Close",
        line=dict(width=2, color="#4F8BF9")
    ))

    fig.add_trace(go.Scatter(
        x=df.index, y=df["EMA20"],
        mode="lines",
        name="EMA20",
        line=dict(width=2, color="#F39C12")
    ))

    # ===========================
    # 2) RSI (Secondary Axis)
    # ===========================
    fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"],
        mode="lines",
        name="RSI",
        line=dict(width=2, color="#00D9A8"),
        yaxis="y2"
    ))

    # Overbought / Oversold
    fig.add_hline(y=70, line_dash="dash", line_color="red", yref="y2")
    fig.add_hline(y=30, line_dash="dash", line_color="green", yref="y2")

    # ===========================
    # 3) MACD & Signal (Third Axis)
    # ===========================
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD"],
        mode="lines",
        name="MACD",
        line=dict(width=2, color="#9B59B6"),
        yaxis="y3"
    ))

    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD_SIGNAL"],
        mode="lines",
        name="Signal",
        line=dict(width=2, color="#E74C3C"),
        yaxis="y3"
    ))

    # ===========================
    # Layout
    # ===========================
    fig.update_layout(
        template="plotly_dark",
        height=700,
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis=dict(
            title="Price",
            showgrid=True
        ),
        yaxis2=dict(
            title="RSI",
            overlaying="y",
            side="right",
            range=[0, 100],
            showgrid=False
        ),
        yaxis3=dict(
            title="MACD",
            anchor="free",
            overlaying="y",
            side="right",
            position=1.1,
            showgrid=False
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02
        )
    )

    st.plotly_chart(fig, use_container_width=True)
