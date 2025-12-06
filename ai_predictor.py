import pandas as pd
import joblib
from features.feature_engineering import add_features

FEATURES = [
    "return", "sma5", "sma10", "ema5", "ema10",
    "rsi", "macd", "signal", "vol_change", "body"
]

class AIPredictor:

    def __init__(self, model_path="direction_model.pkl"):
        self.model = joblib.load(model_path)

    def predict_direction(self, df_original):
        #"""
        #Predict UP/DOWN probability from last row.
        #"""
        df = add_features(df_original.copy())

        latest = df.iloc[-1:][FEATURES]

        proba_up = self.model.predict_proba(latest)[0][1]
        direction = "UP" if proba_up > 0.5 else "DOWN"

        return direction, float(proba_up)


if __name__ == "__main__":
    import yfinance as yf
    df = yf.download("BTC-USD", interval="15m", period="5d")
    predictor = AIPredictor()
    direction, prob = predictor.predict_direction(df)
    print(direction, prob)
