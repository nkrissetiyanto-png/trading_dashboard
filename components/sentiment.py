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


def badge(text, color):
    return f"""<span style="background-color:{color}; padding:4px 10px; border-radius:8px; color:white; font-size:12px; font-weight:600; display:inline-block;">{text}</span>"""


def premium_card(title, value, sub_html="", icon="💠"):
    return f"""
    <div style="
        padding:18px;
        border-radius:18px;
        background:rgba(255,255,255,0.05);
        border:1px solid rgba(255,255,255,0.15);
        backdrop-filter:blur(10px);
        box-shadow:0 4px 14px rgba(0,0,0,0.25);
        text-align:center;
    ">
        <p style="font-size:15px; color:#DFE6F0; font-weight:600; margin-bottom:6px;">
            {icon} {title}
        </p>
        <p style="font-size:32px; font-weight:700; color:white; margin-top:-4px;">
            {value}
        </p>
        <div style="font-size:13px; color:#AAB4C2; margin-top:8px;">
            {sub_html}
        </div>
    </div>
    """

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
    #st.markdown("### 🇮🇩 IHSG Sentiment")

    #if ihsg is None:
    #    st.warning("IHSG data unavailable.")
    #else:
    #    icon = "🟢" if ihsg > 0 else "🔴"
    #    st.markdown(f"**{icon} IHSG Change:** {ihsg:.2f}%")

    # -------------------------------
    #st.write Sector
    # -------------------------------
    #st.markdown("### 🏭 Sector Sentiment")

    #st.write(f"**Sector:** {sector}")
    #st.write(f"**Sector Score:** {sector_score:.0f}/100")

    # ---- Layout ----
    c1, c2, c3, c4 = st.columns(4)

    # === CARD 1: Fear & Greed ===
    with c1:
        #st.markdown("### 🇮🇩 IHSG Sentiment")
        
        if ihsg is None:
            val = "IHSG data unavailable."
        else:
            icon = "🟢" if ihsg > 0 else "🔴"
            val = f"**{icon} IHSG Change:** {ihsg:.2f}%"

        html = premium_card("🇮🇩 IHSG Sentiment", f"{ihsg:.2f}%", val, icon)
        st.markdown(html, unsafe_allow_html=True)

    # === CARD 2: BTC Dominance (hanya BTC) ===
    with c2:
        html = premium_card("🏭 Sector Sentiment", f"{sector_score:.0f}/100", f"**Sector:** {sector}", icon="")
        st.markdown(html, unsafe_allow_html=True)

    # === CARD 3: Coin Momentum ===
    with c3:
        #val = f"{momentum:.2f}%" if momentum is not None else "N/A"
        #col = "#2ecc71" if (momentum is not None and momentum > 0) else "#e74c3c"
        #sub = badge(
        #    "Bullish" if (momentum is not None and momentum > 0) else "Bearish",
        #    col,
        #)
        #title = f"{symbol} Momentum (7d)"
        #html = premium_card(title, val, sub_html=sub, icon=mom_icon)
        st.markdown(html, unsafe_allow_html=True)

    # === CARD 4: Volume Pulse ===
    with c4:
        #val = f"{pulse:.2f}%" if pulse is not None else "N/A"
        #col = "#2ecc71" if (pulse is not None and pulse > 0) else "#e74c3c"
        #sub = badge(
        #    "High Liquidity"
        #    if (pulse is not None and pulse > 0)
        #    else "Low Liquidity",
        #    col,
        #)
        #title = f"{symbol} Volume Pulse"
        #html = premium_card(title, val, sub_html=sub, icon=pulse_icon)
        st.markdown(html, unsafe_allow_html=True)
