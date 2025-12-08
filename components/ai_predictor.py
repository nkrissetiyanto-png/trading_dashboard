import numpy as np
import pandas as pd

class AIPredictor:
    """
    Rule-based AI + Explanation
    Menggunakan 4 fitur:
    1. Return 1 candle
    2. Momentum 5 candle
    3. Volume momentum
    4. Candle body strength
    """

    def __init__(self):
        pass

    # -----------------------------
    # Normalisasi kolom OHLCV
    # -----------------------------
    def _normalize_ohlcv(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        col_map = {}

        candidates = {
            "Open": ["open", "o"],
            "High": ["high", "h"],
            "Low": ["low", "l"],
            "Close": ["close", "c", "price", "last"],
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
            raise KeyError(f"Missing OHLCV: {missing}")

        df = df.rename(columns={orig: std for std, orig in col_map.items()})

        for c in ["Open", "High", "Low", "Close", "Volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        return df.dropna()

    # -----------------------------
    # Feature Explanation (array-based)
    # -----------------------------
    def _explain_feats(self, feats):
        ret_1, mom_5, vol_mom, body = feats

        expl = []

        # 1. Return
        if ret_1 > 0:
            expl.append("📈 Return candle terakhir positif.")
        else:
            expl.append("📉 Return candle terakhir negatif.")

        # 2. Momentum 5 candle
        if mom_5 > 0:
            expl.append("🚀 Momentum 5 candle terakhir bullish.")
        else:
            expl.append("🔻 Momentum 5 candle terakhir bearish.")

        # 3. Volume
        if vol_mom > 0:
            expl.append("📊 Volume berada di atas rata-rata (market aktif).")
        else:
            expl.append("💤 Volume di bawah rata-rata (market lemah).")

        # 4. Body strength
        if body > 0:
            expl.append("💚 Candle body bullish (close > open).")
        else:
            expl.append("❤️ Candle body bearish (close < open).")

        return expl

    # -----------------------------
    # Feature extraction
    # -----------------------------
    def _extract_features(self, df: pd.DataFrame):
        df = self._normalize_ohlcv(df)

        close = df["Close"].values
        volume = df["Volume"].values
        open_ = df["Open"].values
        last = len(df) - 1

        # Return 1 candle
        if last >= 1 and close[last - 1] != 0:
            ret_1 = (close[last] - close[last - 1]) / close[last - 1] * 100
        else:
            ret_1 = 0.0

        # Momentum 5 candle
        if last >= 5 and close[last - 5] != 0:
            mom_5 = (close[last] - close[last - 5]) / close[last - 5] * 100
        else:
            mom_5 = ret_1

        # Volume momentum
        start_idx = max(0, last - 20)
        base_vol = np.nanmean(volume[start_idx:last+1])
        vol_mom = ((volume[last] - base_vol) / base_vol * 100) if base_vol else 0.0

        # Candle body
        body = (close[last] - open_[last]) / open_[last] * 100 if open_[last] else 0.0

        return np.array([ret_1, mom_5, vol_mom, body])

    # -----------------------------
    # Main prediction
    # -----------------------------
    def predict(self, df):
        if df is None or len(df) < 5:
            return {
                "direction": "N/A",
                "prob_up": 0,
                "prob_down": 0,
                "confidence": 0,
                "explanations": ["❗ Data terlalu sedikit untuk AI analisis."]
            }

        # Extract features
        feats = self._extract_features(df)

        # Explanation (based on features)
        explanations = self._explain_feats(feats)

        # Score
        score = sum(1 for x in feats if x > 0)
        prob_up = score / 4
        prob_down = 1 - prob_up
        direction = "UP" if prob_up >= 0.5 else "DOWN"
        confidence = abs(prob_up - prob_down)

        return {
            "direction": direction,
            "prob_up": float(prob_up),
            "prob_down": float(prob_down),
            "confidence": float(confidence),
            "explanations": explanations
        }
