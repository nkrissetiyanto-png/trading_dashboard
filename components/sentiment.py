import streamlit as st
import yfinance as yf
import pandas as pd

# ============================================================

# 🔷 Konfigurasi Saham & Sektor

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

```
"TLKM.JK": "Telco",
"ISAT.JK": "Telco",

"ASII.JK": "Automotive",
"UNTR.JK": "Automotive",

"UNVR.JK": "Consumer",
"ICBP.JK": "Consumer",
"INDF.JK": "Consumer",

"ADRO.JK": "Energy",
"BYAN.JK": "Energy",
```

}

SECTOR_COMPONENTS = {
"Finance": ["BBRI.JK","BBCA.JK","BMRI.JK","BBNI.JK"],
"Telco": ["TLKM.JK","ISAT.JK"],
"Automotive": ["ASII.JK","UNTR.JK"],
"Consumer": ["UNVR.JK","ICBP.JK","INDF.JK"],
"Energy": ["ADRO.JK","BYAN.JK"],
}

# ============================================================

# 🔷 Fungsi Sentimen Saham (Stock Sentiment)

# ============================================================

def get_stock_sentiment(symbol):
"""Menghitung sentimen saham berdasarkan trend, momentum, volatilitas, dan volume."""
df = yf.download(symbol, period="30d", interval="1d")

```
if df.empty:
    return None

df = df.reset_index()

# Minimum data agar aman
if len(df) < 7:
    return None

close = df["Close"]

# ===== Trend (EMA5 vs EMA20)
df["EMA5"] = close.ewm(span=5).mean()
df["EMA20"] = close.ewm(span=20).mean()
trend_score = 20 if df["EMA5"].iloc[-1] > df["EMA20"].iloc[-1] else 5

# ===== Momentum 5 Hari
try:
    mom = float((close.iloc[-1] - close.iloc[-6]) / close.iloc[-6] * 100)
except:
    mom = 0
mom_score = min(max(mom + 10, 0), 20)

# ===== Volatilitas
vol = close.pct_change().std() * 100
vol_score = 20 - min(vol, 20)

# ===== Volume Pressure
try:
    vp = float((df["Volume"].iloc[-1] - df["Volume"].mean()) / df["Volume"].mean() * 100)
except:
    vp = 0
vp_score = min(max(vp + 10, 0), 20)

# Total skor 0–100
total = trend_score + mom_score + vol_score + vp_score
return max(0, min(int(total), 100))
```

# ============================================================

# 🔷 Fungsi Sentimen Sektor (Sector Sentiment)

# ============================================================

def get_sector_sentiment(symbol):
"""Menghitung sentimen sektor berdasarkan rata-rata perubahan komponen sektornya."""
sector = SECTOR_MAP.get(symbol)
if sector is None:
return None, None

```
tickers = SECTOR_COMPONENTS.get(sector, [])
if not tickers:
    return sector, None

changes = []

for t in tickers:
    df = yf.download(t, period="5d", interval="1d")
    if df.empty:
        continue

    df = df.reset_index()
    if len(df) < 2:
        continue

    prev = float(df["Close"].iloc[-2])
    last = float(df["Close"].iloc[-1])

    if prev <= 0:
        continue

    pct = (last - prev) / prev * 100
    changes.append(float(pct))

if len(changes) == 0:
    return sector, None

avg_change = sum(changes) / len(changes)

# Convert to score 0–100
score = (avg_change + 5) * 10
return sector, max(0, min(round(score), 100))
```

# ============================================================

# 🔷 Fungsi Sentimen Market (IHSG)

# ============================================================

def get_sentiment_index():
"""Mengembalikan perubahan harian IHSG & nilai penutupannya."""
df = yf.download("^JKSE", period="10d", interval="1d")
if df.empty:
return None

```
df = df.reset_index()
df["change"] = df["Close"].pct_change() * 100

last_change = df["change"].iloc[-1]
last_close = df["Close"].iloc[-1]

change_val = 0 if pd.isna(last_change) else float(last_change)
return {
    "change": round(change_val, 2),
    "close": round(float(last_close), 2)
}
```

# ============================================================

# 🔷 Market Strength (LQ45 movement)

# ============================================================

def get_sector_strength():
"""Menghitung kekuatan pasar berbasis saham LQ45."""
changes = []

```
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
        if prev <= 0:
            continue

        pct = (last - prev) / prev * 100
        changes.append(float(pct))

    except:
        continue

if len(changes) == 0:
    return None

avg = sum(changes) / len(changes)

# Convert ke skor 0–100
score = (avg + 5) * 10
return max(0, min(round(score), 100))
```

# ============================================================

# 🔷 RENDER SENTIMENT (UI Streamlit)

# ============================================================

def render_sentiment(symbol):
st.subheader("🧭 Sentimen Pasar Indonesia")

```
# ---------- Market ----------
ihsg = get_sentiment_index()
market_score = get_sector_strength()

if ihsg is None or market_score is None:
    st.warning("Tidak dapat memuat sentimen pasar.")
    return

# ---------- Sector ----------
sector, sector_score = get_sector_sentiment(symbol)

# ---------- Stock ----------
stock_score = get_stock_sentiment(symbol)

# ---------- Mood ----------
if market_score >= 70:
    mood = "🟢 Bullish"
elif market_score >= 40:
    mood = "🟡 Netral"
else:
    mood = "🔴 Bearish"

# ---------- UI ----------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Market Sentiment", f"{market_score}/100", mood)

with col2:
    if sector_score is not None:
        st.metric(f"{sector} Sector", f"{sector_score}/100")
    else:
        st.metric("Sector", "N/A")

with col3:
    if stock_score is not None:
        st.metric(f"{symbol} Sentiment", f"{stock_score}/100")
    else:
        st.metric("Stock", "N/A")

# Progress Bar
st.progress(market_score)
```
