import yfinance as yf
import pandas as pd
import requests


def load_candles(symbol, interval, mode="Crypto"):
    # ====== CRYPTO (BINANCE) ======
    # ====== CRYPTO (MEXC) ======
    if mode.startswith("Crypto"):
        url = (
            "https://api.mexc.com/api/v3/klines"
            f"?symbol={symbol}&interval={interval}&limit=200"
        )
    
        resp = requests.get(url, timeout=10)
    
        if resp.status_code != 200:
            raise ValueError(f"MEXC HTTP {resp.status_code}: {resp.text[:200]}")
    
        try:
            data = resp.json()
        except ValueError:
            raise ValueError(f"MEXC non-JSON response: {resp.text[:200]}")
    
        if not isinstance(data, list):
            raise ValueError(f"MEXC API error: {data}")
    
        if not data:
            raise ValueError("MEXC returned empty data")
    
        # Susunan kline MEXC → IDENTIK dengan Binance
        cols = [
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "num_trades",
            "taker_base_vol", "taker_quote_vol", "ignore"
        ]
    
        data = [row[:12] for row in data]
    
        df = pd.DataFrame(data, columns=cols)
        df = df[["open_time", "open", "high", "low", "close", "volume"]]
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df.rename(columns={"open_time": "date"}, inplace=True)
    
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)
    
        return df

    # ====== SAHAM INDONESIA (YFINANCE) ======
    else:
        # Yahoo Finance tidak support 1m untuk IDX → paksa minimal 5m
        if interval == "1m":
            interval = "5m"

        df = yf.download(symbol, period="5d", interval=interval)

        if df.empty:
            raise ValueError(f"Yahoo Finance tidak mengembalikan data untuk {symbol} ({interval})")

        df = df.reset_index()
        df.columns = ["date", "open", "high", "low", "close", "adj", "volume"]
        return df
