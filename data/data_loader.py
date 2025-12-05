import yfinance as yf
import pandas as pd
import requests


def load_candles(symbol, interval, mode="Crypto"):
    # ====== CRYPTO (BINANCE) ======
    # ====== CRYPTO (MEXC) ======
    # ====== CRYPTO VIA MEXC ======
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
        except:
            raise ValueError(f"MEXC non-JSON response: {resp.text[:200]}")

        if not isinstance(data, list):
            raise ValueError(f"MEXC API error: {data}")

        if len(data) == 0:
            raise ValueError("MEXC returned empty data")

        # MEXC returns **8 columns only**
        cols = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume"
        ]

        # Ensure each row has exactly 8 columns
        cleaned = []
        for row in data:
            if len(row) >= 8:
                cleaned.append(row[:8])
            else:
                raise ValueError(f"MEXC returned invalid row length: {row}")

        df = pd.DataFrame(cleaned, columns=cols)

        # Convert timestamps
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df.rename(columns={"open_time": "date"}, inplace=True)

        # Convert numbers
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)

        return df

    # ====== SAHAM INDONESIA (YFINANCE) ======
    else:
        # Yahoo Finance tidak support 1m untuk IDX
        if interval == "1m":
            interval = "5m"
    
        df = yf.download(symbol, period="5d", interval=interval)
    
        if df.empty:
            raise ValueError(f"Yahoo Finance tidak mengembalikan data untuk {symbol} ({interval})")
    
        df = df.reset_index()
    
        # Beberapa interval TIDAK punya 'Adj Close'
        # jadi kita adaptasikan rename ke kolom yang tersedia
        cols = list(df.columns)
    
        # Kasus umum:
        # ['Date','Open','High','Low','Close','Adj Close','Volume']
        if len(cols) == 7:
            df.columns = ["date", "open", "high", "low", "close", "adj", "volume"]
    
        # Kasus interval intraday (TIDAK ada Adj Close)
        # ['Date','Open','High','Low','Close','Volume']
        elif len(cols) == 6:
            df.columns = ["date", "open", "high", "low", "close", "volume"]
            df["adj"] = df["close"]  # tambahkan adj agar konsisten
            df = df[["date","open","high","low","close","adj","volume"]]
    
        else:
            raise ValueError(f"Tidak dikenali struktur kolom dari YFinance: {cols}")
    
        return df
