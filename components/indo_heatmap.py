import streamlit as st
import numpy as np
import pandas as pd


def _safe_float(x):
    try:
        x = float(x)
        if np.isnan(x):
            return None
        return x
    except Exception:
        return None


def _normalize(v, low=-80, high=80):
    """Normalisasi nilai menjadi 0–100 untuk heatmap."""
    v = _safe_float(v)
    if v is None:
        return 50
    if v <= low:
        return 0
    if v >= high:
        return 100
    return int((v - low) / (high - low) * 100)


def compute_heatmap_factors(df: pd.DataFrame):
    """Proxy faktor broker heatmap."""

    df = df.copy()

    if df is None or len(df) < 25:
        return {
            "Volume Spike": 50,
            "Volatility": 50,
            "Body Strength": 50,
            "VWAP Distance": 50,
        }

    required = ["Open", "High", "Low", "Close", "Volume"]
    for col in required:
        if col not in df.columns:
            return {
                "Volume Spike": 50,
                "Volatility": 50,
                "Body Strength": 50,
                "VWAP Distance": 50,
            }

    # Volume spike
    vol = df["Volume"].astype(float)
    vol_ma = vol.rolling(20).mean().iloc[-1]
    vol_last = vol.iloc[-1]

    if vol_ma and not np.isnan(vol_ma):
        vol_spike_pct = (vol_last - vol_ma) / vol_ma * 100
    else:
        vol_spike_pct = 0.0

    # Volatility expansion
    rng = (df["High"] - df["Low"]).astype(float)
    rng_ma = rng.rolling(20).mean().iloc[-1]
    rng_last = rng.iloc[-1]

    if rng_ma and not np.isnan(rng_ma):
        vol_exp_pct = (rng_last - rng_ma) / rng_ma * 100
    else:
        vol_exp_pct = 0.0

    # Body strength
    o = df["Open"].astype(float).iloc[-1]
    c = df["Close"].astype(float).iloc[-1]
    body_pct = (c - o) / o * 100 if o != 0 else 0.0

    # VWAP distance
    vol_cum = vol.cumsum()
    price_vol = (df["Close"].astype(float) * vol).cumsum()

    with np.errstate(divide="ignore", invalid="ignore"):
        vwap = np.where(vol_cum != 0, price_vol / vol_cum, np.nan)

    vwap_last = vwap[-1]
    if not np.isnan(vwap_last) and vwap_last != 0:
        vwap_dist_pct = (c - vwap_last) / vwap_last * 100
    else:
        vwap_dist_pct = 0.0

    return {
        "Volume Spike": _normalize(vol_spike_pct),
        "Volatility": _normalize(vol_exp_pct),
        "Body Strength": _normalize(body_pct),
        "VWAP Distance": _normalize(vwap_dist_pct),
    }


def render_heatmap(df: pd.DataFrame):
    st.markdown("### 🔥 Broker Summary Heatmap (Premium Proxy)")

    data = compute_heatmap_factors(df)
    cols = st.columns(len(data))

    for i, (label, score) in enumerate(data.items()):
        r = int(255 - score * 2.55)
        g = int(score * 2.55)
        color = f"rgba({r},{g},90,0.85)"

        with cols[i]:
            st.markdown(
                f"""
                <div style="
                    padding:14px;
                    border-radius:14px;
                    background:{color};
                    text-align:center;
                    color:white;
                    font-weight:700;
                    box-shadow:0 4px 12px rgba(0,0,0,0.35);
                ">
                    <div style="font-size:13px;opacity:0.9;">{label}</div>
                    <div style="font-size:20px;margin-top:4px;">{score}/100</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
