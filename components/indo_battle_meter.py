import streamlit as st
import yfinance as yf
import numpy as np


def _safe_float(x):
    try:
        x = float(x)
        if np.isnan(x):
            return None
        return x
    except Exception:
        return None


def _get_change(ticker: str):
    """Aman mengambil perubahan % harian via yfinance."""
    try:
        df = yf.download(ticker, period="7d", interval="1d")
        if df is None or df.empty:
            return None

        close = df["Close"].dropna()
        if len(close) < 2:
            return None

        last = _safe_float(close.iloc[-1])
        prev = _safe_float(close.iloc[-2])
        if last is None or prev is None or prev == 0:
            return None

        return (last - prev) / prev * 100
    except Exception:
        return None


def _norm_score(x, clip=5):
    """Normalisasi nilai percent ke skala 0–100."""
    x = _safe_float(x)
    if x is None:
        return 50

    x = max(-clip, min(clip, x))
    return int(50 + (x / clip) * 50)


def compute_battle_score():
    """Foreign vs Domestic power scoring"""

    eido = _get_change("EIDO")
    usdidr = _get_change("USDIDR=X")
    dxy = _get_change("DX-Y.NYB")

    s_eido = _norm_score(eido)
    s_fx = _norm_score(-usdidr if usdidr is not None else None)
    s_dxy = _norm_score(-dxy if dxy is not None else None)

    score = 0.5 * s_eido + 0.3 * s_fx + 0.2 * s_dxy
    return int(score)


def render_battle_meter():
    st.markdown("### ⚔️ Domestic vs Foreign Battle Meter (Premium)")

    score = compute_battle_score()

    if score > 60:
        status = "🟢 Foreign Buying Dominant"
    elif score < 40:
        status = "🔴 Foreign Selling Dominant"
    else:
        status = "⚪ Balanced Flow"

    st.markdown(f"""
        <div style="padding:18px;border-radius:16px;background:rgba(15,23,42,0.9);border:1px solid rgba(148,163,184,0.4);box-shadow:0 6px 20px rgba(0,0,0,0.45);">
            <div style="color:#e5e7eb;font-size:15px;margin-bottom:6px;">
                Foreign Strength Meter
            </div>
            <div style="margin-top:8px;color:#e5e7eb;font-size:14px;">
                Score: <b>{score}/100</b><br>{status}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    ) 
    
    
