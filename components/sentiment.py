import streamlit as st
import yfinance as yf
import pandas as pd
from components.foreign_flow import get_foreign_flow

# ============================================================
#  🔷 Konfigurasi Saham & Sektor
# ============================================================

LQ45 = [
    "BBCA.JK","BBRI.JK","BMRI.JK","BBNI.JK","ASII.JK","TLKM.JK",
    "UNVR.JK","ICBP.JK","INDF.JK","AMRT.JK"
]

SECTOR_MAP = {
    "BBRI.JK": "Finance",
    "BBCA.JK": "Finance",
    "BMRI.JK": "Finance",
    "BBNI.JK": "Finance",

    "TLKM.JK": "Telco",
    "ISAT.JK": "Telco",

    "ASII.JK": "Automotive",
    "UNTR.JK": "Automotive",

    "UNVR.JK": "Consumer",
    "ICBP.JK": "Consumer",
    "INDF.JK": "Consumer",

    "ADRO.JK": "Energy",
    "BYAN.JK": "Energy",
}

SECTOR_COMPONENTS = {
    "Finance": ["BBRI.JK","BBCA.JK","BMRI.JK","BBNI.JK"],
    "Telco": ["TLKM.JK","ISAT.JK"],
    "Automotive": ["ASII.JK","UNTR.JK"],
    "Consumer": ["UNVR.JK","ICBP.JK","INDF.JK"],
    "Energy": ["ADRO.JK","BYAN.JK"],
}

# ============================================================
#  🔷 Fungsi Sentimen Saham
# ============================================================

def get_stock_sentiment(symbol):
    df = yf.download(symbol, period="30d", interval="1d")
    if df.empty:
        return None

    df = df.reset_index()

    if len(df) < 7:
        return None

    close = df["Close"]

    # ==== Trend (EMA)
    df["EMA5"] = close.ewm(span=5).mean()
    df["EMA20"] = close.ewm(span=20).mean()
    trend_score = 20 if float(df["EMA5"].iloc[-1]) > float(df["EMA20"].iloc[-1]) else 5

    # ==== Momentum
    try:
        mom = float((close.iloc[-1] - close.iloc[-6]) / close.iloc[-6] * 100)
    except:
        mom = 0.0
    mom_score = min(max(mom + 10, 0), 20)

    # ==== Volatilitas
    try:
        vol_raw = close.pct_change().std()
        vol = float(vol_raw) if vol_raw is not None else 0.0
    except:
        vol = 0.0
    vol_score = 20 - min(vol, 20)

    # ==== Volume Pressure
    try:
        vp_raw = (df["Volume"].iloc[-1] - df["Volume"].mean()) / df["Volume"].mean() * 100
        vp = float(vp_raw)
    except:
        vp = 0.0
    vp_score = min(max(vp + 10, 0), 20)

    # ==== Total Score 0–100
    total = trend_score + mom_score + vol_score + vp_score
    total = max(0, min(int(total), 100))

    return total

# ============================================================
#  🔷 Fungsi Sentimen Sektor
# ============================================================
def get_sector_sentiment(symbol):
    """
    Return sektor + skor sentimen (0—100).
    """
    try:
        # Mapping sektor
        sector_map = {
            "BBRI.JK": "Finance",
            "BBNI.JK": "Finance",
            "BMRI.JK": "Finance",
            "BBCA.JK": "Finance",
            "ASII.JK": "Automotive",
            "UNVR.JK": "Consumer",
            "ICBP.JK": "Consumer",
            "TLKM.JK": "Telecommunication",
            "ISAT.JK": "Telecommunication",
            "GGRM.JK": "Tobacco",
            "HMSP.JK": "Tobacco",
        }

        sector_name = sector_map.get(symbol.upper(), "General")

        # Ambil data sektor terkait → jika gagal, score None
        ticker = f"{symbol}"
        df = yf.download(ticker, period="5d", interval="1d")

        if df.empty:
            return sector_name, None

        change = (df["Close"].iloc[-1] - df["Close"].iloc[0]) / df["Close"].iloc[0] * 100
        score = 50 + change   # normalisasi sederhana

        # Jika score gagal dihitung
        if score is None or np.isnan(score):
            return sector_name, None

        # Clamp 0-100
        score = max(0, min(round(float(score)), 100))

        return sector_name, score

    except Exception as e:
        print("Sector sentiment error:", e)
        return "General", None

# ============================================================
#  🔷 Fungsi IHSG Index Sentiment
# ============================================================

def get_sentiment_index():
    df = yf.download("^JKSE", period="10d", interval="1d")
    if df.empty:
        return None

    df = df.reset_index()
    df["change"] = df["Close"].pct_change() * 100

    change = df["change"].iloc[-1]
    if pd.isna(change):
        change = 0

    return {
        "change": round(float(change), 2),
        "close": round(float(df["Close"].iloc[-1]), 2)
    }


# ============================================================
#  🔷 Market Strength (LQ45)
# ============================================================

def get_sector_strength():
    changes = []
    for sym in LQ45:
        try:
            df = yf.download(sym, period="3d", interval="1d")
            if df.empty or "Close" not in df.columns:
                continue

            df = df.reset_index()
            if len(df) < 2:
                continue

            prev = float(df["Close"].iloc[-2])
            last = float(df["Close"].iloc[-1])
            pct = (last - prev) / prev * 100
            changes.append(pct)
        except:
            continue

    if len(changes) == 0:
        return None

    avg = sum(changes) / len(changes)
    return max(0, min(round((avg + 5) * 10), 100))


# ============================================================
#  🔷 Render Sentimen UI
# ============================================================

def render_sentiment(symbol):
    st.subheader("🧭 Sentimen Pasar Indonesia")

    ihsg = get_sentiment_index()
    market_score = get_sector_strength()

    # ====== IHSG Info (Ditampilkan duluan seperti versi awal) ======
    col_ihsg1, col_ihsg2 = st.columns(2)
    
    change = ihsg["change"]
    is_up = change >= 0
    
    badge = (
        f"<span style='color:#00ff88; font-weight:600;'>🟢 +{change}%</span>"
        if is_up else
        f"<span style='color:#ff5555; font-weight:600;'>🔴 {change}%</span>"
    )
    
    with col_ihsg1:
        st.metric("IHSG", ihsg["close"])
        #st.markdown(badge, unsafe_allow_html=True)
    
    with col_ihsg2:
        st.metric("Perubahan Harian", f"{change}%")

    
    if ihsg is None or market_score is None:
        st.warning("Tidak dapat memuat sentimen pasar.")
        return

    sector, sector_score = get_sector_sentiment(symbol)
    stock_score = get_stock_sentiment(symbol)

    if market_score >= 70:
        mood = "🟢 Bullish"
    elif market_score >= 40:
        mood = "🟡 Netral"
    else:
        mood = "🔴 Bearish"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Market Sentiment", f"{market_score}/100", mood)

    with col2:
        st.metric(f"{sector} Sector" if sector_score else "Sector", 
                  f"{sector_score}/100" if sector_score else "N/A")

    with col3:
        st.metric(f"{symbol} Sentiment", 
                  f"{stock_score}/100" if stock_score else "N/A")

    st.progress(market_score)
    
    # === Foreign Flow ===
    flow_score, flow_bias, eido_chg, rupiah_chg, vol_ratio = get_foreign_flow()

    st.markdown("### 🌍 Foreign Flow (Investor Asing)")
    
    # Safe formatting
    eido_val   = f"{eido_chg:.2f}%" if isinstance(eido_chg, (int, float)) else "N/A"
    rupiah_val = f"{rupiah_chg:.2f}%" if isinstance(rupiah_chg, (int, float)) else "N/A"
    vol_val    = f"{vol_ratio:.2f}%" if isinstance(vol_ratio, (int, float)) else "N/A"
    
    score_val = f"{flow_score}/100" if flow_score is not None else "N/A"
    
    st.metric("Foreign Flow Score", score_val)
    st.write(f"**Status:** {flow_bias}")
    
    st.write(f"- EIDO Change: {eido_val}")
    st.write(f"- Rupiah Strength: {rupiah_val}")
    st.write(f"- IHSG Volume Ratio: {vol_val}")
