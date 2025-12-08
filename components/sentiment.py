import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd

# ============================================================
# SAFE UTILITIES
# ============================================================

def safe_float(x):
    try:
        x = float(x)
        if np.isnan(x):
            return None
        return x
    except:
        return None


# ============================================================
# 1) IHSG SENTIMENT
# ============================================================

def get_ihsg_sentiment():
    """
    Mengambil perubahan IHSG (1-day change %) dengan aman.
    """
    try:
        df = yf.download("^JKSE", period="10d", interval="1d")

        if df is None or df.empty:
            return None

        close = df["Close"].dropna()
        if len(close) < 2:
            return None

        last = safe_float(close.iloc[-1])
        prev = safe_float(close.iloc[-2])

        if last is None or prev is None or prev == 0:
            return None

        change = (last - prev) / prev * 100
        return round(change, 2)

    except Exception:
        return None


# ============================================================
# 2) SECTOR SENTIMENT
# ============================================================

SECTOR_MAP = {
    "Finance": ["BBRI.JK", "BBCA.JK", "BMRI.JK", "BBNI.JK"],
    "Telco": ["TLKM.JK", "ISAT.JK"],
    "Consumer": ["UNVR.JK", "ICBP.JK", "INDF.JK"],
    "Retail": ["AMRT.JK", "MAPI.JK"],
    "Energy": ["PGAS.JK", "MEDC.JK"],
}

def get_sector_sentiment(symbol):
    """
    Hitung sentiment sektor berdasarkan saham-saham rekan satu sektor.
    Aman walaupun data kosong.
    """
    symbol = symbol.upper()
    sector_name = None

    # cari sektor dari symbol
    for sec, syms in SECTOR_MAP.items():
        if symbol in syms:
            sector_name = sec
            break

    if sector_name is None:
        return "Unknown", 50  # netral

    scores = []

    for s in SECTOR_MAP[sector_name]:
        try:
            df = yf.download(s, period="7d", interval="1d")
            close = df["Close"].dropna()

            if len(close) < 2:
                continue

            last = safe_float(close.iloc[-1])
            prev = safe_float(close.iloc[-2])

            if last is None or prev is None or prev == 0:
                continue

            change = (last - prev) / prev * 100
            scores.append(change)

        except:
            continue

    # Jika semua gagal → netral
    if len(scores) == 0:
        return sector_name, 50

    avg = float(np.mean(scores))

    # Normalisasi → 0–100
    score = max(0, min(round((avg + 3) * 10), 100))
    return sector_name, score


# ============================================================
# 3) FOREIGN FLOW (ANTI BIAS)
# ============================================================

def get_foreign_flow():
    """
    Ambil data proxy foreign flow dari EIDO.
    Jika kosong → fallback ke FXI (ETF Emerging Markets).

    Return dalam bentuk % perubahan harian.
    """
    def fetch_etf(etf_symbol):
        try:
            df = yf.download(etf_symbol, period="7d", interval="1d")
            if df is None or df.empty:
                return None

            close = df["Close"].dropna()
            if len(close) < 2:
                return None

            last = safe_float(close.iloc[-1])
            prev = safe_float(close.iloc[-2])

            if prev is None or prev == 0:
                return None

            return round((last - prev) / prev * 100, 2)
        except:
            return None

    # 1) Coba EIDO
    eido = fetch_etf("EIDO")
    if eido is not None:
        return eido

    # 2) fallback ke FXI (lebih likuid)
    fxi = fetch_etf("FXI")
    if fxi is not None:
        return fxi

    # 3) fallback final → netral
    return 0.0


# ============================================================
# 4) MARKET MOOD SUMMARY
# ============================================================

def interpret_sentiment(value):
    """
    Mengubah angka menjadi label mood.
    """
    if value is None:
        return "Unknown"

    if value > 1:
        return "Bullish"
    elif value < -1:
        return "Bearish"
    else:
        return "Neutral"


# ============================================================
# 5) RENDER SENTIMENT UI
# ============================================================

def render_sentiment(symbol):
    st.subheader("📊 Indonesian Market Sentiment (Premium)")

    # -------------------------------
    # Load data
    # -------------------------------
    ihsg = get_ihsg_sentiment()
    sector, sector_score = get_sector_sentiment(symbol)
    foreign = get_foreign_flow()

    # -------------------------------
    # Display IHSG
    # -------------------------------
    st.markdown("### 🇮🇩 IHSG Sentiment")

    if ihsg is None:
        st.warning("IHSG data unavailable.")
    else:
        icon = "🟢" if ihsg > 0 else "🔴"
        st.markdown(f"**{icon} IHSG Change:** {ihsg:.2f}%")

    # -------------------------------
    # Display Sector
    # -------------------------------
    st.markdown("### 🏭 Sector Sentiment")

    st.write(f"**Sector:** {sector}")
    st.write(f"**Sector Score:** {sector_score:.0f}/100")

    # -------------------------------
    # Display Foreign Flow
    # -------------------------------
    st.markdown("### 🌏 Foreign Flow")

    icon = "🟢" if foreign > 0 else "🔴" if foreign < 0 else "⚪"
    st.write(f"**{icon} Foreign ETF Change:** {foreign:.2f}%")

    # -------------------------------
    # Final Mood Summary
    # -------------------------------
    st.markdown("### 🔮 Market Mood Summary")

    msgs = []

    if ihsg is not None:
        msgs.append(f"IHSG is **{interpret_sentiment(ihsg)}** ({ihsg:+.2f}%).")

    msgs.append(f"Sector sentiment is **{sector_score}/100**.")
    msgs.append(f"Foreign flow indicates **{interpret_sentiment(foreign)}** ({foreign:+.2f}%).")

    for m in msgs:
        st.markdown(f"- {m}")

    st.markdown("---")
