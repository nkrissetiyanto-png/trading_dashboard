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

    def detect_reversal(self, df):
        """
        AI Reversal Detector
        Mengembalikan:
        - type: 'bullish', 'bearish', atau None
        - score: probabilitas 0-1
        - reasons: list penjelasan
        """

        df = self._normalize_ohlcv(df)
        if len(df) < 20:
            return {"type": None, "score": 0.0, "reasons": []}

        #start revision
        #close = df["Close"].values
        #open_ = df["Open"].values
        #volume = df["Volume"].values
        
        # Auto-detect volume column
        vol_col = None
        for c in df.columns:
            if c.lower() in ["volume", "vol", "qty"]:
                vol_col = c
                break
        
        if vol_col is None:
            print("WARNING: No volume column detected → using constant volume placeholder.")
            df["volume_safe"] = 1
            vol_col = "volume_safe"
        
        close = df["Close"].values
        open_  = df["Open"].values
        volume = df[vol_col].values
        #end revision

        
        last = len(df) - 1
        reasons = []
        score = 0

        # ---------- 1. RSI reversal ----------
        # compute RSI 14
        delta = np.diff(close)
        gain = np.maximum(delta, 0)
        loss = np.abs(np.minimum(delta, 0))

        avg_gain = gain[-14:].mean() if len(gain) >= 14 else 0
        avg_loss = loss[-14:].mean() if len(loss) >= 14 else 0

        if avg_loss == 0:
            rsi = 50
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        # RSI oversold → bullish reversal
        if rsi < 30:
            score += 1
            reasons.append("RSI extremely low → oversold condition")

        # RSI overbought → bearish reversal
        if rsi > 70:
            score += 1
            reasons.append("RSI extremely high → overbought condition")

        # ---------- 2. Volume exhaustion ----------
        base_vol = np.mean(volume[last-10:last])
        if base_vol > 0:
            vol_ratio = volume[last] / base_vol
        else:
            vol_ratio = 1

        if vol_ratio < 0.7:
            score += 1
            reasons.append("Volume exhaustion detected → trend weakening")

        # ---------- 3. Candle body compression ----------
        body = abs(close[last] - open_[last])
        avg_body = np.mean(np.abs(close[last-10:last] - open_[last-10:last]))

        if avg_body > 0 and body < avg_body * 0.4:
            score += 1
            reasons.append("Candle compression → market preparing reversal")

        # ---------- 4. Trend momentum ----------
        if last >= 5:
            mom = (close[last] - close[last-5]) / close[last-5] * 100
        else:
            mom = 0

        if mom < -1:
            type_ = "bullish"    # downtrend losing steam
            score += 1
        elif mom > 1:
            type_ = "bearish"    # uptrend losing steam
            score += 1
        else:
            type_ = None

        prob = min(score / 5, 1)

        return {
            "type": type_,
            "score": float(prob),
            "reasons": reasons
        }

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
    def _extract_features(self, df: pd.DataFrame) -> np.ndarray:
    df = self._normalize_ohlcv(df)

    # ================== ENSURE CLEAN DF ==================
    # Drop baris yang incomplete (indikator bisa bikin NaN di awal)
    df = df.dropna(subset=["Open", "Close", "Volume"], how="any")

    # Tidak cukup data?
    if len(df) < 10:
        return np.array([0, 0, 0, 0])
    # =====================================================

    # Auto-detect volume column
    vol_col = None
    for c in df.columns:
        if c.lower() in ["volume", "vol", "qty"]:
            vol_col = c
            break
    if vol_col is None:
        df["volume_safe"] = 1
        vol_col = "volume_safe"

    close = df["Close"]
    volume = df[vol_col]
    open_ = df["Open"]

    last = -1

    # Return last candle
    try:
        ret_1 = ((close.iloc[last] - close.iloc[last - 1]) / close.iloc[last - 1] * 100)
    except:
        ret_1 = 0.0

    # Momentum 5 candle
    try:
        mom_5 = ((close.iloc[last] - close.iloc[last - 5]) / close.iloc[last - 5] * 100)
    except:
        mom_5 = ret_1

    # Volume momentum
    try:
        base_vol = volume.iloc[last-20:last].mean()
        vol_mom = ((volume.iloc[last] - base_vol) / base_vol * 100) if base_vol else 0.0
    except:
        vol_mom = 0.0

    # Candle body strength
    try:
        body = ((close.iloc[last] - open_.iloc[last]) / open_.iloc[last] * 100)
    except:
        body = 0.0

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
