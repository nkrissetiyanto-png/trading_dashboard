import streamlit as st
import numpy as np

def detect_reversal(df, sensitivity="Medium"):
    """
    Reversal detector berbasis:
    - RSI extreme
    - Candle compression
    - Momentum exhaustion
    - Volume exhaustion
    Sensitivity menentukan threshold.
    """
    df = df.copy()

    if len(df) < 10:
        return None, "Not enough data"

    close = df["Close"].values
    open_ = df["Open"].values
    volume = df["Volume"].values

    last = len(close) - 1

    body = abs(close[last] - open_[last])
    prev_body = abs(close[last-1] - open_[last-1])

    # Momentum 5 candle
    mom5 = (close[last] - close[last-5]) / close[last-5] * 100 if last >= 5 else 0

    # Volume ratio
    vol_ratio = volume[last] / (np.mean(volume[last-10:last]) + 1e-9)

    # ============================
    # Sensitivity Level
    # ============================

    if sensitivity == "Low":
        rsi_high = 75
        rsi_low = 25
        body_compress_factor = 0.35
        vol_exhaust_low = 0.7
        mom_exhaust = 0.5

    elif sensitivity == "High":
        rsi_high = 65
        rsi_low = 35
        body_compress_factor = 0.75
        vol_exhaust_low = 0.9
        mom_exhaust = 1.5

    else:  # Medium
        rsi_high = 70
        rsi_low = 30
        body_compress_factor = 0.55
        vol_exhaust_low = 0.8
        mom_exhaust = 1.0

    # ============================
    # RULES
    # ============================

    explanations = []
    reversal = None

    # Rule 1 — RSI extreme
    if "rsi" in df.columns:
        rsi_last = df["rsi"].iloc[-1]
        if rsi_last > rsi_high:
            reversal = "DOWN"
            explanations.append(f"RSI overbought ({rsi_last:.2f})")
        elif rsi_last < rsi_low:
            reversal = "UP"
            explanations.append(f"RSI oversold ({rsi_last:.2f})")

    # Rule 2 — Body compression (candle kecil setelah candle besar)
    if prev_body > 0 and (body / prev_body) < body_compress_factor:
        if close[last] < open_[last]:
            reversal = "DOWN"
            explanations.append("Candle compression bearish")
        else:
            reversal = "UP"
            explanations.append("Candle compression bullish")

    # Rule 3 — Volume exhaustion
    if vol_ratio < vol_exhaust_low:
        explanations.append(f"Volume exhaustion (vol ratio {vol_ratio:.2f})")

    # Rule 4 — Momentum exhaustion
    if abs(mom5) < mom_exhaust:
        explanations.append(f"Momentum exhaustion ({mom5:.2f}%)")

    # Final decision
    if reversal is None:
        return None, ["No clear reversal detected"]

    return reversal, explanations
