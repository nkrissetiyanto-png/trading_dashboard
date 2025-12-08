import yfinance as yf
import numpy as np
import pandas as pd


def get_foreign_flow():
    """
    Menghitung Foreign Flow berdasarkan:
    1. EIDO ETF (proxy asing global)
    2. USDIDR pair strength
    3. IHSG volume expansion
    """

    try:
        # -------------------------------
        # 1) EIDO ETF (iShares Indonesia ETF)
        # -------------------------------
        eido = yf.download("EIDO", period="5d", interval="1d")

        if not eido.empty and len(eido) >= 2:
            eido_change = (eido["Close"].iloc[-1] - eido["Close"].iloc[-2]) / eido["Close"].iloc[-2] * 100
        else:
            eido_change = 0

        # Skor EIDO (max 40)
        if eido_change > 0:
            eido_score = min(40, eido_change * 5)
        else:
            eido_score = max(-40, eido_change * 5)

        # -------------------------------
        # 2) USDIDR Strength
        # -------------------------------
        usdidr = yf.download("USDIDR=X", period="7d", interval="1d")
        if not usdidr.empty and len(usdidr) >= 2:
            rupiah_change = (usdidr["Close"].iloc[-2] - usdidr["Close"].iloc[-1]) / usdidr["Close"].iloc[-2] * 100
        else:
            rupiah_change = 0

        # Skor Rupiah (max 40)
        if rupiah_change > 0:
            rupiah_score = min(40, rupiah_change * 5)
        else:
            rupiah_score = max(-40, rupiah_change * 5)

        # -------------------------------
        # 3) IHSG Volume Expansion
        # -------------------------------
        ihsg = yf.download("^JKSE", period="30d", interval="1d")

        if not ihsg.empty and len(ihsg) >= 20:
            vol = ihsg["Volume"].iloc[-1]
            vol_ma = ihsg["Volume"].rolling(20).mean().iloc[-1]

            if vol_ma > 0:
                vol_ratio = (vol - vol_ma) / vol_ma * 100
            else:
                vol_ratio = 0
        else:
            vol_ratio = 0

        # Skor Volume (max 20)
        if vol_ratio > 0:
            vol_score = min(20, vol_ratio * 0.2)
        else:
            vol_score = max(-20, vol_ratio * 0.2)

        # -------------------------------
        # FINAL SCORE
        # -------------------------------
        total_score = eido_score + rupiah_score + vol_score

        # Normalisasi ke 0-100
        norm = (total_score + 100) / 200 * 100
        norm = max(0, min(100, norm))

        if norm > 60:
            bias = "Bullish (Asing Masuk)"
        elif norm < 40:
            bias = "Bearish (Asing Keluar)"
        else:
            bias = "Neutral"

        return round(norm, 2), bias, eido_change, rupiah_change, vol_ratio

    except Exception as e:
        print("Foreign Flow Error:", e)
        return None, "N/A", None, None, None
