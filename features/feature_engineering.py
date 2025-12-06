import pandas as pd
import ta

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add technical indicators as ML features.
    """
    df = df.copy()

    df["return"] = df["Close"].pct_change()

    df["sma5"] = df["Close"].rolling(5).mean()
    df["sma10"] = df["Close"].rolling(10).mean()

    df["ema5"] = df["Close"].ewm(span=5).mean()
    df["ema10"] = df["Close"].ewm(span=10).mean()

    df["rsi"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()

    macd = ta.trend.MACD(df["Close"])
    df["macd"] = macd.macd()
    df["signal"] = macd.macd_signal()

    df["vol_change"] = df["Volume"].pct_change()

    df["body"] = (df["Close"] - df["Open"]) / df["Open"]

    df["Close_next"] = df["Close"].shift(-1)
    df["Direction"] = (df["Close_next"] > df["Close"]).astype(int)

    df.dropna(inplace=True)
    return df


if __name__ == "__main__":
    df = pd.read_csv("crypto_15m_raw.csv")
    df = add_features(df)
    df.to_csv("crypto_15m_features.csv", index=False)
    print("📁 Saved crypto_15m_features.csv")
