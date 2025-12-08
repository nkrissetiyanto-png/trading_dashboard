import numpy as np
import pandas as pd

class AIPredictor:
    """
    Simple rule-based AI (tanpa sklearn, tanpa .pkl).
    Otomatis deteksi nama kolom open/high/low/close/volume (case-insensitive).
    """

    def __init__(self):
        pass

    # ---------- Utility: normalisasi nama kolom ----------
    def _normalize_ohlcv(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Mencari kolom OHLCV dengan nama bervariasi (open / Open / close / price / dll),
        lalu merename ke standar: Open, High, Low, Close, Volume.
        """
        df = df.copy()
        col_map = {}

        candidates = {
            "Open":   ["open", "o"],
            "High":   ["high", "h"],
            "Low":    ["low", "l"],
            "Close":  ["close", "c", "price", "last"],
            "Volume": ["volume", "vol", "qty"],
        }

        lower_cols = {c.lower(): c for c in df.columns}

        for std_name, poss in candidates.items():
            for p in poss:
                if p.lower() in lower_cols:
                    col_map[std_name] = lower_cols[p.lower()]
                    break

        missing = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c not in col_map]
        if missing:
            # Kalau benar-benar tidak ketemu, lempar error supaya bisa di-handle di predict()
            raise KeyError(f"Missing OHLCV columns: {missing}. Available: {list(df.columns)}")

        # Rename ke standar
        df = df.rename(columns={orig: std for std, orig in col_map.items()})

        # Pastikan numeric
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["Open", "Close"])
        return df

    # ---------- Feature extraction ----------
    def _extract_features(self, df: pd.DataFrame) -> np.ndarray:
        df = self._normalize_ohlcv(df)

        if len(df) < 2:
            return np.array([0.0, 0.0, 0.0, 0.0])

        close = df["Close"].values
        volume = df["Volume"].values
        open_ = df["Open"].values

        last = len(df) - 1

        # Return 1 candle terakhir
        if last >= 1 and close[last - 1] != 0:
            ret_1 = (close[last] - close[last - 1]) / close[last - 1] * 100
        else:
            ret_1 = 0.0

        # Momentum 5 candle
        if last >= 5 and close[last - 5] != 0:
            mom_5 = (close[last] - close[last - 5]) / close[last - 5] * 100
        else:
            mom_5 = ret_1

        # Volume momentum (dibanding rata-rata 20 candle terakhir)
        start_idx = max(0, last - 20)
        base_vol = np.nanmean(volume[start_idx:last + 1])
        if base_vol and not np.isnan(base_vol):
            vol_mom = (volume[last] - base_vol) / base_vol * 100
        else:
            vol_mom = 0.0

        # Candle body strength
        if open_[last] != 0:
            body = (close[last] - open_[last]) / open_[last] * 100
        else:
            body = 0.0

        return np.array([ret_1, mom_5, vol_mom, body])

    # ---------- Main predict ----------
    def predict(self, df: pd.DataFrame):
        # Minimal data supaya indikator ada konteks
        if df is None or len(df) < 5:
            return {
                "direction": "N/A",
                "prob_up": 0.0,
                "prob_down": 0.0,
                "confidence": 0.0,
            }

        try:
            feats = self._extract_features(df)
        except Exception as e:
            # Log di console Streamlit, tapi jangan bikin app crash
            print("AI feature error:", e)
            return {
                "direction": "N/A",
                "prob_up": 0.0,
                "prob_down": 0.0,
                "confidence": 0.0,
            }

        # Scoring sederhana: berapa banyak fitur yang bullish (>0)
        score = 0
        total = 4

        if feats[0] > 0:  # return 1 candle
            score += 1
        if feats[1] > 0:  # momentum 5 candle
            score += 1
        if feats[2] > 0:  # volume momentum
            score += 1
        if feats[3] > 0:  # body strength
            score += 1

        prob_up = score / total
        prob_down = 1 - prob_up
        direction = "UP" if prob_up >= 0.5 else "DOWN"
        confidence = abs(prob_up - prob_down)

        return {
            "direction": direction,
            "prob_up": float(prob_up),
            "prob_down": float(prob_down),
            "confidence": float(confidence),
        }
