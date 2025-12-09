import numpy as np
import pandas as pd

# ============================================================
#  UTIL — AUTO NORMALIZE OHLCV
# ============================================================

def normalize_ohlcv(df: pd.DataFrame):
    df = df.copy()
    lower = {c.lower(): c for c in df.columns}

    mapping = {
        "Open":   ["open", "o"],
        "High":   ["high", "h"],
        "Low":    ["low", "l"],
        "Close":  ["close", "c", "price", "last"],
        "Volume": ["volume", "vol", "qty"],
    }

    remap = {}
    for std, poss in mapping.items():
        for p in poss:
            if p in lower:
                remap[std] = lower[p]
                break

    # Fail-safe: if something missing
    for key in ["Open", "High", "Low", "Close", "Volume"]:
        if key not in remap:
            raise KeyError(f"Missing column: {key}")

    df = df.rename(columns={v: k for k, v in remap.items()})

    # numeric ensure
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.dropna(subset=["Open", "Close"])
    

# ============================================================
#  PREMIUM REVERSAL DETECTOR
# ============================================================

def premium_reversal(df: pd.DataFrame):
    """
    Menghasilkan:
    - probability (0–100)
    - direction: UP / DOWN / NEUTRAL
    - confidence (0–1)
    - explanations[]
    """

    explanations = []
    try:
        df = normalize_ohlcv(df)
    except Exception as e:
        return 0, "NEUTRAL", 0.0, [f"Data error: {e}"]

    n = len(df)
    min_req = max(14, int(n * 0.15))  # dynamic minimum
    if n < min_req:
        return 0, "NEUTRAL", 0.0, [f"Data insufficient: {n}/{min_req} candles"]

    # ------------------------------------------------------------
    # 1) RSI Proxy
    # ------------------------------------------------------------
    df["chg"] = df["Close"].diff()
    df["up"]  = df["chg"].clip(lower=0)
    df["dn"]  = -df["chg"].clip(upper=0)
    rs = df["up"].rolling(14).mean() / df["dn"].rolling(14).mean()
    rsi = 100 - (100 / (1 + rs))
    last_rsi = rsi.iloc[-1]

    # ------------------------------------------------------------
    # 2) Candle Body Power
    # ------------------------------------------------------------
    body = df["Close"].iloc[-1] - df["Open"].iloc[-1]
    body_pct = body / df["Open"].iloc[-1] * 100

    # ------------------------------------------------------------
    # 3) Volume Anomaly (vs 20 bars)
    # ------------------------------------------------------------
    vol_base = df["Volume"].rolling(20).mean().iloc[-1]
    vol_ratio = (
        df["Volume"].iloc[-1] / vol_base if vol_base and not np.isnan(vol_base) else 1
    )

    # ------------------------------------------------------------
    # 4) Volatility Compression / Expansion
    # ------------------------------------------------------------
    df["range"] = df["High"] - df["Low"]
    volat = df["range"].rolling(10).mean().iloc[-1]
    last_vol = df["range"].iloc[-1]
    vol_expansion = last_vol > volat * 1.2

    # ------------------------------------------------------------
    # PREMIUM WEIGHTED SCORING
    # ------------------------------------------------------------
    score = 0

    # RSI
    if last_rsi < 30:
        score += 2
        explanations.append("🟢 RSI Oversold → UP reversal bias")
    elif last_rsi > 70:
        score -= 2
        explanations.append("🔴 RSI Overbought → DOWN reversal bias")
    else:
        explanations.append("⚪ RSI neutral")

    # Candle Body
    if body_pct > 1:
        score += 1
        explanations.append("📈 Bullish candle body")
    elif body_pct < -1:
        score -= 1
        explanations.append("📉 Bearish candle body")

    # Volume Spike
    if vol_ratio > 1.4:
        explanations.append("💥 Volume spike detected")
        score += 1 if body_pct > 0 else -1

    # Volatility Expansion
    if vol_expansion:
        explanations.append("⚡ Volatility expansion → strong shift potential")
        score += 1 if body_pct > 0 else -1

    # ------------------------------------------------------------
    # FINAL OUTPUT
    # ------------------------------------------------------------
    prob = int(min(100, max(0, (score + 4) * 12.5)))  # scale
    confidence = abs(prob - 50) / 50  # 0–1

    if prob > 58:
        direction = "UP"
    elif prob < 42:
        direction = "DOWN"
    else:
        direction = "NEUTRAL"

    return prob, direction, confidence, explanations
