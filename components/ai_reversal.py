import numpy as np
import pandas as pd

def _normalize_ohlcv(df):
    df = df.copy()
    col_map = {}
    candidates = {
        "Open": ["open", "o"],
        "High": ["high", "h"],
        "Low": ["low", "l"],
        "Close": ["close", "c", "price", "last"],
        "Volume": ["volume", "vol", "qty"],
    }

    lower = {c.lower(): c for c in df.columns}

    for std, poss in candidates.items():
        for p in poss:
            if p.lower() in lower:
                col_map[std] = lower[p.lower()]
                break

    missing = [c for c in ["Open", "High", "Low", "Close"] if c not in col_map]
    if missing:
        raise KeyError(f"Missing columns: {missing}")

    df = df.rename(columns={orig: std for std, orig in col_map.items()})

    for col in ["Open", "High", "Low", "Close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Open", "Close"])
    return df


def detect_reversal(df, sensitivity=1.0):
    """
    sensitivity:
        1.0 = normal
        2.0 = lebih sensitif
        0.5 = lebih konservatif
    """
    explanations = []

    try:
        df = _normalize_ohlcv(df)
    except Exception as e:
        return None, [f"Data error: {e}"]

    # Convert sensitivity to float safely
    try:
        sensitivity = float(sensitivity)
    except:
        sensitivity = 1.0

    if len(df) < 5:
        return None, ["Data terlalu sedikit untuk reversal analysis."]

    row = df.iloc[-1]

    open_ = row["Open"]
    close = row["Close"]
    high = row["High"]
    low = row["Low"]

    body = abs(close - open_)
    upper_wick = high - max(open_, close)
    lower_wick = min(open_, close) - low

    # Hindari pembagian nol
    body = body if body > 0 else 0.0001

    # ============================
    # 🔻 BEARISH REVERSAL
    # Syarat:
    # - long upper wick
    # - body kecil
    # ============================
    cond_bearish = upper_wick > body * (2.0 * sensitivity)

    # ============================
    # 🔺 BULLISH REVERSAL
    # Syarat:
    # - long lower wick
    # - body kecil
    # ============================
    cond_bullish = lower_wick > body * (2.0 * sensitivity)

    # Build explanation
    explanations.append(f"Body size: {body:.4f}")
    explanations.append(f"Upper wick: {upper_wick:.4f}")
    explanations.append(f"Lower wick: {lower_wick:.4f}")
    explanations.append(f"Sensitivity factor: {sensitivity}")

    if cond_bullish and not cond_bearish:
        explanations.append("Long lower wick terdeteksi → potensi bullish reversal.")
        return "UP", explanations

    if cond_bearish and not cond_bullish:
        explanations.append("Long upper wick terdeteksi → potensi bearish reversal.")
        return "DOWN", explanations

    explanations.append("Tidak ada wick ekstrem → no clear reversal.")
    return None, explanations
