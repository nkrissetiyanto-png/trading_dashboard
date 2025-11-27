import yfinance as yf
import pandas as pd
import requests

def load_candles(symbol, interval, mode="Crypto"):

    if mode.startswith("Crypto"):
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=200"
        data = requests.get(url).json()

        df = pd.DataFrame(data)
        df = df.iloc[:, :6]
        df.columns = ["date", "open", "high", "low", "close", "volume"]
        df["date"] = pd.to_datetime(df["date"], unit="ms")
        df = df.astype({
            "open": float,
            "high": float,
            "low": float,
            "close": float,
            "volume": float
        })
        return df

    else:
        if interval == "1m":
            interval = "5m"
        
        df = yf.download(symbol, period="5d", interval=interval)
        df = df.reset_index()
        df.columns = ["date", "open", "high", "low", "close", "adj", "volume"]
        return df
