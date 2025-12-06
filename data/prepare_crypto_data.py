import yfinance as yf
import pandas as pd

def download_crypto_15m(symbol="BTC-USD", period="60d"):
    df = yf.download(symbol, interval="15m", period=period)
    df.dropna(inplace=True)
    df.to_csv("data/crypto_raw_15m.csv")
    print("📁 Saved: data/crypto_raw_15m.csv")

if __name__ == "__main__":
    download_crypto_15m()
