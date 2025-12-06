
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv("data/crypto_features_15m.csv")

FEATURES = ["return","sma5","sma10","ema5","ema10","rsi","macd","signal","vol_change","body"]
X = df[FEATURES]
y = df["Direction"]

model = RandomForestClassifier(
    n_estimators=400,
    max_depth=12,
    random_state=42
)

model.fit(X, y)
joblib.dump(model, "models/crypto_ai_model.pkl")

print("🎯 Model saved: models/crypto_ai_model.pkl")
