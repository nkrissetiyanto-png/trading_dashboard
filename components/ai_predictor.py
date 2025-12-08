import numpy as np
import pandas as pd

class AIPredictor:
    """
    Simple rule-based AI (no sklearn, no model file).
    Menggunakan 4 fitur:
    - return 1 candle terakhir
    - momentum 5 candle
    - volume momentum
    - candle body strength
    """

    def __init__(self):
        pass

    def _extract_features(self, df: pd.DataFrame) -> np.ndarray:
        df = df.copy()

        # Paksa kolom numeric
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            if col not in df.columns:
                raise KeyError(f"Missing column: {col}")
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df.dropna(subset=["Open", "Close", "Volume"], inplace=True)

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

        # Volume momentum (bandingkan dengan rata-rata 20 candle)
        start_idx = max(0, last - 20)
        base_vol = np.mean(volume[start_idx:last + 1])
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

    def predict(self, df: pd.DataFrame):
        # Minimal 10 data biar indikator ada sedikit konteks
        if df is None or len(df) < 10:
            return {
                "direction": "N/A",
                "prob_up": 0.0,
                "prob_down": 0.0,
                "confidence": 0.0,
            }

        try:
            feats = self._extract_features(df)
        except Exception as e:
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

        if feats[0] > 0:  # return
            score += 1
        if feats[1] > 0:  # momentum
            score += 1
        if feats[2] > 0:  # volume
            score += 1
        if feats[3] > 0:  # body
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

