import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

FEATURES = [
    "return", "sma5", "sma10", "ema5", "ema10",
    "rsi", "macd", "signal", "vol_change", "body"
]

def load_dataset():
    df = pd.read_csv("crypto_15m_features.csv")
    df = df.dropna()
    return df


def train_model():
    df = load_dataset()

    X = df[FEATURES]
    y = df["Direction"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = RandomForestClassifier(
        n_estimators=250,
        max_depth=10,
        random_state=42,
        class_weight="balanced"
    )

    print("🧠 Training model...")
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print("\n📊 Evaluation:")
    print(classification_report(y_test, preds))
    print(f"🎯 Accuracy: {acc:.4f}")

    joblib.dump(model, "direction_model.pkl")
    print("💾 Model saved as direction_model.pkl")


if __name__ == "__main__":
    train_model()
