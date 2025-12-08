import streamlit as st
from components.ai_predictor import AIPredictor
from components.ai_reversal import detect_reversal
from components.smartmoney import compute_smart_money

def final_decision_engine(df, trend_result, sensitivity=1.0):

    reversal_signal, reversal_expl = detect_reversal(df, sensitivity)
    smart = compute_smart_money(df)

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
            "Reversal hammer detected",
            "Smart money inflow" if smart == "BULLISH" else "Market still healthy",
        ]

    # Strong SELL
    elif trend_dir == "DOWN" and reversal_signal == "DOWN":
        decision = "SELL"
        reason = [
            "Trend bearish",
            "Bearish wick reversal detected",
            "Smart money outflow" if smart == "BEARISH" else "Volume weakening",
        ]

    # EARLY BUY (bottom reversal)
    elif trend_dir == "DOWN" and reversal_signal == "UP":
        decision = "REVERSAL BUY"
        reason = [
            "Trend masih turun tetapi muncul hammer",
            "Potensi pembalikan arah",
            "Momentum kemungkinan berubah",
        ]

    # EARLY SELL (top reversal)
    elif trend_dir == "UP" and reversal_signal == "DOWN":
        decision = "TAKE PROFIT"
        reason = [
            "Trend naik tetapi muncul shooting star",
            "Potensi market top → pembalikan mungkin terjadi",
        ]

    # No alignment → WAIT
    else:
        decision = "WAIT"
        reason = ["Tidak ada sinyal kuat", "Trend dan reversal tidak sinkron"]

    return decision, reason, reversal_signal, smart
