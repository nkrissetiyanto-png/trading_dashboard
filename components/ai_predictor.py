import numpy as np
import pandas as pd
from components.feature_engineering import add_features

class AIPredictor:
    def __init__(self):
        pass

    def predict(self, df):
        """
        AI fallback (rule-based).
        Works even without sklearn or .pkl model.
        """

        if df is None or len(df) < 20:
            return {
                "direction": "N/A",
                "prob_up": 0.0,
                "prob_down": 0.0,
                "confidence": 0.0
            }

        # Tambah fitur ML
        try:
            df = add_features(df.copy())
        except Exception as e:
            print("Feature engineering error:", e)
            return {
                "direction": "N/A",
                "prob_up": 0.0,
                "prob_down": 0.0,
                "confidence": 0.0
            }

        last = df.iloc[-1]

        signals = []

        # Return momentum
        signals.append(1 if last["return"] > 0 else 0)

        # RSI
        if last["rsi"] < 30:
            signals.append(1)
        elif last["rsi"] > 70:
            signals.append(0)

        # MACD crossover
        signals.append(1 if last["macd"] > last["signal"] else 0)

        # Volume expansion
        signals.append(1 if last["vol_change"] > 0 else 0)

        score = np.mean(signals)

        direction = "UP" if score >= 0.5 else "DOWN"
        prob_up = float(score)
        prob_down = float(1 - score)

        return {
            "direction": direction,
            "prob_up": prob_up,
            "prob_down": prob_down,
            "confidence": abs(prob_up - prob_down)
        }
