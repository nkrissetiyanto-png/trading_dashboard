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
        """
        Return:
            ("UP"/"DOWN", probability)
        """

        feats = self._extract_features(df).reshape(1, -1)

        try:
            feats_scaled = self.scaler.transform(feats)
            prob = self.model.predict_proba(feats_scaled)[0][1]  # prob of UP
        except:
            prob = 0.5

        direction = "UP" if prob >= 0.5 else "DOWN"

        return direction, prob
