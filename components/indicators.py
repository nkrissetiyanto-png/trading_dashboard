import streamlit as st
import plotly.graph_objects as go
import numpy as np

# ============================================================
# INDICATORS
# ============================================================

def EMA(series, period):
    return series.ewm(span=period, adjust=False).mean()

def RSI(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(span=period).mean()
    loss = (-delta.clip(upper=0)).ewm(span=period).mean()
    rsi = 100 - (100 / (1 + gain / loss))
    return rsi

def MACD(series):
    fast = EMA(series, 12)
    slow = EMA(series, 26)
    macd = fast - slow
    signal = EMA(macd, 9)
    hist = macd - signal
    return macd, signal, hist

# ============================================================
# AI COMMENTARY
# ============================================================

def ai_indicator_commentary(df):
    rsi = df["RSI"].iloc[-1]
    macd = df["MACD"].iloc[-1]
    sig = df["MACD_SIGNAL"].iloc[-1]
    close = df["close"].iloc[-1]
    ema20 = df["EMA20"].iloc[-1]

    notes = []

    # EMA Trend
    if close > ema20:
        notes.append("Harga berada **di atas EMA20** → market short-term bullish.")
    else:
        notes.append("Harga berada **di bawah EMA20** → short-term bearish momentum.")

    # RSI
    if rsi > 70:
        notes.append("RSI menunjukkan kondisi **overbought** – potensi koreksi.")
    elif rsi < 30:
        notes.append("RSI **oversold** – peluang technical rebound.")
    else:
        notes.append("RSI normal, market **tidak jenuh**.")

    # MACD
    if macd > sig:
        notes.append("MACD **bullish crossover** → momentum naik menguat.")
    else:
        notes.append("MACD **bearish crossover** → momentum melemah.")

    # Combine
    summary = " ".join(notes)
    return f"### 🧠 AI Market Insight\n{summary}"

# ============================================================
# PREMIUM LEVEL 3 RENDERER
# ============================================================

def render_indicators_premium_level3(df):

    st.subheader("🚀 Technical Indicators Premium Level 3 (Ultra)")

    # compute indicators
    df["EMA20"] = EMA(df["close"], 20)
    df["RSI"] = RSI(df["close"])
    df["MACD"], df["MACD_SIGNAL"], df["MACD_HIST"] = MACD(df["close"])

    fig = go.Figure()

    # ====================================================================
    # 1) PRICE + EMA (Glow + Gradient Shadow)
    # ====================================================================
    # Shadow glow for Close
    fig.add_trace(go.Scatter(
        x=df.index, y=df["close"],
        mode="lines",
        name="Close",
        line=dict(width=2, color="#7AB6FF"),
        hovertemplate="Close: %{y}<extra></extra>"
    ))

    # EMA glow
    fig.add_trace(go.Scatter(
        x=df.index, y=df["EMA20"],
        mode="lines",
        name="EMA20",
        line=dict(width=3, color="#FFB84D"),
        hovertemplate="EMA20: %{y}<extra></extra>"
    ))

    # ====================================================================
    # 2) RSI (Neon Green, Glow)
    # ====================================================================
    fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"],
        mode="lines",
        name="RSI",
        line=dict(width=3, color="#00FFAA"),
        yaxis="y2",
        hovertemplate="RSI: %{y}<extra></extra>"
    ))

    fig.add_hline(y=70, line_dash="dash", line_color="red", yref="y2")
    fig.add_hline(y=30, line_dash="dash", line_color="green", yref="y2")

    # ====================================================================
    # 3) MACD (Neon Purple / Red + Histogram)
    # ====================================================================
    # Histogram
    fig.add_trace(go.Bar(
        x=df.index,
        y=df["MACD_HIST"],
        name="MACD Histogram",
        marker_color=np.where(df["MACD_HIST"] > 0, "#AA7BFF", "#FF6F6F"),
        yaxis="y3",
        opacity=0.45,
        hovertemplate="Hist: %{y}<extra></extra>"
    ))

    # MACD Line
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD"],
        mode="lines",
        name="MACD",
        line=dict(width=3, color="#B388FF"),
        yaxis="y3"
    ))

    # Signal Line
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD_SIGNAL"],
        mode="lines",
        name="Signal",
        line=dict(width=3, color="#FF7676"),
        yaxis="y3"
    ))

    # ====================================================================
    # LAYOUT — Dark Neon Premium Theme
    # ====================================================================
    fig.update_layout(
        template="plotly_dark",
        height=800,
        margin=dict(l=20, r=40, t=40, b=20),
        paper_bgcolor="rgba(14,17,23,1)",
        plot_bgcolor="rgba(14,17,23,1)",

        yaxis=dict(
            title="Price",
            showgrid=False,
            zeroline=False
        ),
        yaxis2=dict(
            title="RSI",
            overlaying="y",
            side="right",
            range=[0, 100],
            showgrid=False,
            zeroline=False
        ),
        yaxis3=dict(
            title="MACD",
            anchor="free",
            overlaying="y",
            side="right",
            position=1.08,
            showgrid=False,
            zeroline=True
        ),

        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # ====================================================================
    # AI COMMENTARY
    # ====================================================================
    st.markdown(ai_indicator_commentary(df))
