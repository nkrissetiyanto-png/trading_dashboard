import numpy as np
import pandas as pd

# ============================================================
#  NORMALISASI KOLUMN OHLCV  (ANTI ERROR Close / close / price)
# ============================================================

def _normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    col_map = {}

    candidates = {
        "Open":   ["open", "o"],
        "High":   ["high", "h"],
        "Low":    ["low", "l"],
        "Close":  ["close", "c", "price", "last"],
        "Volume": ["volume", "vol", "qty"],
    }

    lower_cols = {col.lower(): col for col in df.columns}

    for std_name, poss in candidates.items():
        for p in poss:
            if p.lower() in lower_cols:
                col_map[std_name] = lower_cols[p.lower()]
                break

    # Kalau ada kolom mandatory yang tidak ditemukan
    missing = [c for c in ["Open", "High", "Low", "Close"] if c not in col_map]
    if missing:
        raise KeyError(f"Missing OHLC columns: {missing}. Available: {list(df.columns)}")

    df = df.rename(columns={orig: new for new, orig in col_map.items()})

    # Pastikan numeric
    for col in ["Open", "High", "Low", "Close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Open", "Close"])
    return df

# ============================================================
#  AI REVERSAL DETECTOR
# ============================================================

def detect_reversal(df: pd.DataFrame, sensitivity: float = 1.0):
    """
    sensitivity (0.5–2.0)
    <1.0 lebih sensitif (lebih banyak sinyal)
    >1.0 lebih ketat (lebih sedikit sinyal)
    """
    explanations = []

    try:
        df = _normalize_ohlcv(df)
    except Exception as e:
        return "NO_SIGNAL", [f"Data error: {e}"]

    if len(df) < 5:
        return "NO_SIGNAL", ["Data terlalu sedikit untuk deteksi reversal."]

    close = df["Close"].values
    high = df["High"].values
    low = df["Low"].values
    open_ = df["Open"].values

    last = len(close) - 1

    # ============================================================
    # HAMMER / PIN BAR BULLISH
    # ============================================================
    body = abs(close[last] - open_[last])
    range_candle = high[last] - low[last]
    lower_wick = open_[last] - low[last] if close[last] > open_[last] else close[last] - low[last]

    if (
        lower_wick > body * (2.5 * sensitivity)
        and close[last] > open_[last]
    ):
        explanations.append("🟢 Bullish hammer terdeteksi.")
        return "REVERSAL_UP", explanations

    # ============================================================
    # SHOOTING STAR / PIN BAR BEARISH
    # ============================================================
    upper_wick = high[last] - close[last] if close[last] > open_[last] else high[last] - open_[last]

    if (
        upper_wick > body * (2.5 * sensitivity)
        and close[last] < open_[last]
    ):
        explanations.append("🔴 Bearish shooting star terdeteksi.")
        return "REVERSAL_DOWN", explanations

    # ============================================================
    # NO CLEAR SIGNAL
    # ============================================================
    return "NO_SIGNAL", ["No clear reversal signal detected."]
