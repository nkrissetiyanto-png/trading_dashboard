import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

class AIPredictor:

    def __init__(self):
        self.model = LogisticRegression()
        self.scaler = StandardScaler()

        # Dummy training (supaya model tidak error saat pertama running)
        X = np.array([[0, 0, 0], [1, 1, 1]])
        y = np.array([0, 1])
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        self.model.fit(X_scaled, y)

    def _extract_features(self, df):
        """
        Feature engineering sederhana:
        - return 3 fitur: price momentum, volume momentum, candle body strength
        """
        close = df["Close"].values
        volume = df["Volume"].values

        # Momentum 1 jam (4 candle 15m)
        if len(close) < 10:
            return np.array([0, 0, 0])

        price_mom = (close[-1] - close[-4]) / close[-4] * 100
        vol_mom = (volume[-1] - np.mean(volume[-10:])) / np.mean(volume[-10:]) * 100
        candle = close[-1] - df["Open"].values[-1]

        return np.array([price_mom, vol_mom, candle])

    def predict(self, df):

        # Safety check
        if df is None or len(df) < 30:
            return {
                "direction": "N/A",
                "prob_up": 0.0,
                "prob_down": 0.0,
                "confidence": 0.0
            }

        # Create features
        try:
            feats = add_features(df.copy())
        except Exception as e:
            print("Feature engineering error:", e)
            return {
                "direction": "N/A",
                "prob_up": 0.0,
                "prob_down": 0.0,
                "confidence": 0.0
            }

        last = feats.iloc[-1]

        # RULE-BASED AI (no ML model)
        score = 0
        total = 4

        # Return momentum
        if last["return"] > 0:
            score += 1

        # MACD
        if last["macd"] > last["signal"]:
            score += 1

        # RSI
        if last["rsi"] < 30:
            score += 1
        elif last["rsi"] > 70:
            score -= 1

        # Volume expansion
        if last["vol_change"] > 0:
            score += 1

        normalized = (score + 1) / total   # convert score range to 0–1
        direction = "UP" if normalized >= 0.5 else "DOWN"

        return {
            "direction": direction,
            "prob_up": float(normalized),
            "prob_down": float(1 - normalized),
            "confidence": abs(0.5 - normalized) * 2
        }
