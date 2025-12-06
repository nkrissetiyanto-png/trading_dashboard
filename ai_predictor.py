import joblib
import pandas as pd
from data.feature_engineering import add_features

MODEL_PATH = "models/crypto_ai_model.pkl"

class AIPredictor:
    def __init__(self):
        try:
            self.model = joblib.load(MODEL_PATH)
            print("🤖 AI Model Loaded Successfully")
        except FileNotFoundError:
            print("⚠️ MODEL NOT FOUND — AI disabled.")
            self.model = None

        self.FEATURES = [
            "return","sma5","sma10","ema5","ema10",
            "rsi","macd","signal","vol_change","body"
        ]

    def predict(self, df):
        if self.model is None:
            return None
        
        df = add_features(df)[-1:]  # last row only
        X = df[self.FEATURES]
        prob = self.model.predict_proba(X)[0]

        return {
            "direction": "UP" if prob[1] > 0.5 else "DOWN",
            "prob_up": float(prob[1]),
            "prob_down": float(prob[0]),
            "confidence": float(abs(prob[1] - prob[0]))
        }
