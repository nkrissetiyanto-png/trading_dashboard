import yfinance as yf
import pandas as pd

def load_candles(symbol, interval):
    df = yf.download(
        tickers=symbol,
        period="5d",
        interval=interval
    )
    df = df.reset_index()
    df.columns = ["date", "open", "high", "low", "close", "adj", "volume"]
    return df
