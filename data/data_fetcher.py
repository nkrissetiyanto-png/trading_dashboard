import yfinance as yf
import pandas as pd

def fetch_crypto_data(symbol="BTC-USD", interval="15m", period="3y"):
    """
    Download historical crypto data for training ML model.
    """
    print(f"📥 Downloading {symbol} ({interval}, {period}) ...")
    df = yf.download(symbol, interval=interval, period=period)

    if df.empty:
        raise ValueError("❌ Failed to download data. Empty dataframe.")

    df.dropna(inplace=True)
    df.reset_index(inplace=True)

    print(f"✅ Download success! Rows: {len(df)}")
    return df


if __name__ == "__main__":
    df = fetch_crypto_data()
    df.to_csv("crypto_15m_raw.csv", index=False)
    print("📁 Saved crypto_15m_raw.csv")
