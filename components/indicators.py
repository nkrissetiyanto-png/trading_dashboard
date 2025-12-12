# components/indicators.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -------------------------
# Utilities: normalize col names
# -------------------------
def _normalize_ohlcv_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure DataFrame has Open, High, Low, Close, Volume columns (capitalized).
    Accepts common variants: open/OPEN/price/last, vol/Volume, etc.
    """
    df = df.copy()
    cols_lower = {c.lower(): c for c in df.columns}

    mapping = {
        "Open": ["open", "o"],
        "High": ["high", "h"],
        "Low": ["low", "l"],
        "Close": ["close", "c", "price", "last"],
        "Volume": ["volume", "vol", "qty"],
    }

    rename_map = {}
    for std, keys in mapping.items():
        for k in keys:
            if k in cols_lower:
                rename_map[cols_lower[k]] = std
                break

    # If Close not present, try 'adjclose' variations:
    if "Close" not in rename_map.values():
        for alt in ["adjclose", "adj_close"]:
            if alt in cols_lower:
                rename_map[cols_lower[alt]] = "Close"
                break

    df = df.rename(columns=rename_map)

    # Ensure numeric and existence
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col not in df.columns:
            raise KeyError(f"Missing required column '{col}'. Available: {list(df.columns)}")
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Open", "Close"])
    return df

# -------------------------
# Indicator functions
# -------------------------
def EMA(series: pd.Series, period: int):
    return series.ewm(span=period, adjust=False).mean()

def SMA(series: pd.Series, period: int):
    return series.rolling(period).mean()

def RSI(series: pd.Series, period: int = 14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up = up.ewm(alpha=1/period, adjust=False).mean()
    ma_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs = ma_up / ma_down
    rsi = 100 - (100 / (1 + rs))
    return rsi

def MACD(series: pd.Series):
    fast = series.ewm(span=12, adjust=False).mean()
    slow = series.ewm(span=26, adjust=False).mean()
    macd = fast - slow
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    return macd, signal, hist

def bollinger_bands(series: pd.Series, period: int = 20, std_mul: float = 2.0):
    sma = series.rolling(period).mean()
    std = series.rolling(period).std()
    upper = sma + std_mul * std
    lower = sma - std_mul * std
    return upper, sma, lower

def stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3):
    low_min = df["Low"].rolling(k_period).min()
    high_max = df["High"].rolling(k_period).max()
    k = 100 * (df["Close"] - low_min) / (high_max - low_min)
    d = k.rolling(d_period).mean()
    return k, d

# -------------------------
# AI Trend overlay (light, rule-based fallback)
# -------------------------
def compute_ai_trend_overlay(df: pd.DataFrame):
    """
    Try to import a heavier AI predictor if present.
    Otherwise compute a simple rule-based 'trend score' using EMA crossover + MACD.
    Returns dict with label and score (0-1).
    """
    # try to get external AIPredictor's score if available
    try:
        from components.ai_predictor import AIPredictor  # optional
        ai = AIPredictor()
        res = ai.predict(df)
        # if returns prob_up/ prob_down use that
        prob_up = res.get("prob_up", None)
        if prob_up is not None:
            return {"label": res.get("direction", "N/A"), "score": float(prob_up)}
    except Exception:
        pass

    # fallback rule-based score (0..1)
    ema20 = EMA(df["Close"], 20).iloc[-1]
    ema50 = EMA(df["Close"], 50).iloc[-1]
    macd, signal, hist = MACD(df["Close"])
    macd_last = macd.iloc[-1]
    signal_last = signal.iloc[-1]

    score = 0.5
    if ema20 > ema50:
        score += 0.2
    else:
        score -= 0.2

    if macd_last > signal_last:
        score += 0.15
    else:
        score -= 0.15

    # normalize to 0..1
    score = max(0.0, min(1.0, score))
    label = "UP" if score >= 0.55 else "DOWN" if score <= 0.45 else "NEUTRAL"
    return {"label": label, "score": score}

# -------------------------
# Main render function (premium level 2)
# -------------------------
def render_indicators(df: pd.DataFrame):
    """
    Premium multi-panel indicators chart:
    - Panel 1: Price, EMA20, EMA50, Bollinger Bands, AI overlay annotation
    - Panel 2: Volume bars + EMA volume
    - Panel 3: RSI + Stochastic (K/D)
    - Panel 4: MACD (macd, signal, hist)
    """
    st.subheader("📊 Technical Indicators — Premium (Level 2)")

    # Normalize columns
    try:
        df = _normalize_ohlcv_cols(df)
    except Exception as e:
        st.error(f"Indicators error: {e}")
        return

    # Ensure index is datetime for plotting
    if not np.issubdtype(df.index.dtype, np.datetime64):
        try:
            df.index = pd.to_datetime(df.index)
        except Exception:
            # if index not parseable, create numeric index
            df = df.reset_index(drop=True)
            df.index.name = "idx"

    # Calculate indicators
    df["EMA20"] = EMA(df["Close"], 20)
    df["EMA50"] = EMA(df["Close"], 50)
    df["SMA200"] = SMA(df["Close"], 200)
    df["BB_UP"], df["BB_MID"], df["BB_LOW"] = bollinger_bands(df["Close"], 20)
    df["RSI"] = RSI(df["Close"], 14)
    df["MACD"], df["MACD_SIGNAL"], df["MACD_HIST"] = MACD(df["Close"])
    df["VOL_EMA20"] = EMA(df["Volume"], 20)
    df["STO_K"], df["STO_D"] = stochastic(df, 14, 3)

    # AI overlay (safe)
    ai_overlay = compute_ai_trend_overlay(df)

    # Build Plotly subplots
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        row_heights=[0.45, 0.12, 0.18, 0.25],
        vertical_spacing=0.02,
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": False}]]
    )

    x = df.index

    # ---------------- Panel 1: Price + EMAs + BB ----------------
    fig.add_trace(go.Candlestick(
        x=x,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Price",
        increasing_line_color="rgba(34,197,94,0.9)",
        decreasing_line_color="rgba(239,68,68,0.9)",
        showlegend=False,
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=x, y=df["EMA20"], name="EMA20", line=dict(width=1.6, dash="solid"),
                             hovertemplate="%{y:.2f}"), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["EMA50"], name="EMA50", line=dict(width=1.2, dash="dot"),
                             hovertemplate="%{y:.2f}"), row=1, col=1)

    # Bollinger bands as filled area
    fig.add_trace(go.Scatter(x=x, y=df["BB_UP"], name="BB Upper", line=dict(width=1), hoverinfo="skip",
                             showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["BB_LOW"], name="BB Lower", line=dict(width=1), fill='tonexty',
                             fillcolor='rgba(255,255,255,0.02)', hoverinfo="skip",
                             showlegend=False), row=1, col=1)
    # mid separately (optional)
    fig.add_trace(go.Scatter(x=x, y=df["BB_MID"], name="BB Mid", line=dict(width=0.9, dash="dash"),
                             line_color="rgba(255,255,255,0.12)", showlegend=False), row=1, col=1)

    # AI overlay annotation (small badge)
    try:
        badge_text = f"AI {ai_overlay['label']} {ai_overlay['score']*100:.0f}%"
        # place annotation at latest candle close
        last_x = x[-1]
        last_y = df["Close"].iloc[-1]
        fig.add_annotation(dict(
            x=last_x, y=last_y,
            xref="x", yref="y",
            text=badge_text,
            showarrow=True,
            arrowhead=1,
            ax=40,
            ay=-40,
            bgcolor="rgba(16,185,129,0.9)" if ai_overlay["label"]=="UP" else ("rgba(239,68,68,0.9)" if ai_overlay["label"]=="DOWN" else "rgba(148,163,184,0.7)"),
            bordercolor="rgba(255,255,255,0.06)",
            font=dict(color="white", size=11)
        ), row=1, col=1)
    except Exception:
        pass

    # ---------------- Panel 2: Volume bars + EMA volume ----------------
    colors = np.where(df["Close"] >= df["Open"], "rgba(34,197,94,0.9)", "rgba(239,68,68,0.9)")
    fig.add_trace(go.Bar(x=x, y=df["Volume"], marker_color=colors, name="Volume", showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["VOL_EMA20"], name="VOL_EMA20", line=dict(width=1.2), line_color="rgba(250,204,21,0.9)"),
                  row=2, col=1)

    # ---------------- Panel 3: RSI + Stochastic ----------------
    fig.add_trace(go.Scatter(x=x, y=df["RSI"], name="RSI", line=dict(width=1.4), line_color="rgba(96,165,250,0.95)"), row=3, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["STO_K"], name="%K", line=dict(width=1.0), line_color="rgba(34,197,94,0.9)"), row=3, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["STO_D"], name="%D", line=dict(width=1.0, dash="dash"), line_color="rgba(239,68,68,0.9)"), row=3, col=1)
    # RSI thresholds
    fig.add_hline(y=70, line=dict(color="rgba(239,68,68,0.4)", width=1, dash="dash"), row=3, col=1)
    fig.add_hline(y=30, line=dict(color="rgba(34,197,94,0.4)", width=1, dash="dash"), row=3, col=1)

    # ---------------- Panel 4: MACD ----------------
    fig.add_trace(go.Scatter(x=x, y=df["MACD"], name="MACD", line=dict(width=1.4), line_color="rgba(99,102,241,0.95)"), row=4, col=1)
    fig.add_trace(go.Scatter(x=x, y=df["MACD_SIGNAL"], name="Signal", line=dict(width=1.0, dash="dash"), line_color="rgba(168,85,247,0.85)"), row=4, col=1)
    # histogram as bar
    hist_colors = np.where(df["MACD_HIST"] >= 0, "rgba(34,197,94,0.7)", "rgba(239,68,68,0.7)")
    fig.add_trace(go.Bar(x=x, y=df["MACD_HIST"], name="MACD Hist", marker_color=hist_colors, opacity=0.6, showlegend=False), row=4, col=1)

    # ---------------- Layout polish ----------------
    fig.update_layout(
        template="plotly_dark",
        height=980,
        margin=dict(l=10, r=10, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Improve x-axis formatting
    fig.update_xaxes(showticklabels=True, rangeslider_visible=False)

    # Y-axis titles and ranges (optional polish)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="Oscillators", row=3, col=1)
    fig.update_yaxes(title_text="MACD", row=4, col=1)

    # Render
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
