from components.ai_reversal import detect_reversal
from components.smartmoney import get_smart_money_bias

def normalize_ohlcv(df):
    df = df.copy()
    mapping = {
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    }

    lower = {c.lower(): c for c in df.columns}

    for std, raw in mapping.items():
        if std in lower:
            df[mapping[std]] = df[lower[std]]

    return df


def final_decision_engine(df, trend_result, sensitivity=1.0):
    df = normalize_ohlcv(df)

    reversal_signal, reversal_expl = detect_reversal(df, sensitivity)
    smart = get_smart_money_bias(df)
    
    trend_dir = trend_result["direction"]
    conf = trend_result["confidence"]

    # ==========================
    # DECISION FUSION LOGIC
    # ==========================

    # Strong BUY
    if trend_dir == "UP" and reversal_signal == "UP":
        decision = "BUY"
        reason = [
            "Trend bullish",
            "Reversal hammer terdeteksi",
            f"Smart Money: {smart}",
        ]

    # Strong SELL
    elif trend_dir == "DOWN" and reversal_signal == "DOWN":
        decision = "SELL"
        reason = [
            "Trend bearish",
            "Reversal bearish wick terdeteksi",
            f"Smart Money: {smart}",
        ]

    # Early BUY
    elif trend_dir == "DOWN" and reversal_signal == "UP":
        decision = "REVERSAL BUY"
        reason = [
            "Trend turun tapi reversal terdeteksi",
            "Potensi pembalikan arah",
        ]

    # Early SELL / Take Profit
    elif trend_dir == "UP" and reversal_signal == "DOWN":
        decision = "TAKE PROFIT"
        reason = [
            "Trend naik tapi reversal bearish terdeteksi",
            "Potensi market top",
        ]

    else:
        decision = "WAIT"
        reason = [
            "Tidak ada alignment antara trend & reversal",
            f"Smart Money: {smart}",
        ]

    return decision, reason, reversal_signal, smart
