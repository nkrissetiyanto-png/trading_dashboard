import pandas as pd
import ta

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --- Pastikan kolom wajib ada ---
    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Missing required column: {col}")

    # Returns
    df["return"] = df["Close"].pct_change()

    # Moving averages
    df["sma5"] = df["Close"].rolling(5).mean()
    df["sma10"] = df["Close"].rolling(10).mean()
    df["ema5"] = df["Close"].ewm(span=5).mean()
    df["ema10"] = df["Close"].ewm(span=10).mean()

    # RSI
    try:
        df["rsi"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()
    except:
        df["rsi"] = 50

    # MACD
    try:
        macd = ta.trend.MACD(df["Close"])
        df["macd"] = macd.macd()
        df["signal"] = macd.macd_signal()
    except:
        df["macd"] = 0
        df["signal"] = 0

    # Volume change
    df["vol_change"] = df["Volume"].pct_change()

    # Candle body strength
    df["body"] = (df["Close"] - df["Open"]) / df["Open"]

    # Next-candle target (label untuk AI)
    df["Close_next"] = df["Close"].shift(-1)
    df["Direction"] = (df["Close_next"] > df["Close"]).astype(int)

    # Clean up
    df.replace([float("inf"), -float("inf")], 0, inplace=True)
    df.fillna(0, inplace=True)

    return df


if __name__ == "__main__":
    df = pd.read_csv("crypto_15m_raw.csv")
    df = add_features(df)
    df.to_csv("crypto_15m_features.csv", index=False)
    print("📁 Saved crypto_15m_features.csv")
