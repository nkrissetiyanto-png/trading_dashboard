import streamlit as st
import numpy as np
import pandas as pd

# ==========================================
# MEMORY for reversal probability history
# ==========================================
def get_memory():
    if "rev_history" not in st.session_state:
        st.session_state.rev_history = []
    return st.session_state.rev_history

def add_history(prob):
    hist = get_memory()
    hist.append(prob)
    if len(hist) > 120:   # simpan max 120 data
        hist.pop(0)

def normalize_ohlcv(df):
    """
    Rename kolom apa pun menjadi: Open, High, Low, Close, Volume
    Aman untuk data saham & crypto.
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

    for std, keys in candidates.items():
        for k in keys:
            if k.lower() in lower_cols:
                col_map[std] = lower_cols[k.lower()]
                break

    # jika ada kolom yang benar2 tidak ditemukan → error
    missing = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c not in col_map]
    if missing:
        raise KeyError(f"Missing OHLCV cols: {missing}. Available: {list(df.columns)}")

    df = df.rename(columns={orig: std for std, orig in col_map.items()})

    # convert to numeric
    for c in ["Open", "High", "Low", "Close", "Volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df.dropna(subset=["Open","High","Low","Close"])

def detect_zones(df):
    df = normalize_ohlcv(df)   # ⬅️ FIX PALING PENTING

    close = df["Close"].values
    high  = df["High"].values
    low   = df["Low"].values

    zones_demand = []
    zones_supply = []

    n = len(df)
    if n < 30:
        return zones_demand, zones_supply

    # swing detection
    for i in range(2, n-2):
        if low[i] < low[i-1] and low[i] < low[i+1]:
            zones_demand.append((low[i], low[i] * 1.003))

        if high[i] > high[i-1] and high[i] > high[i+1]:
            zones_supply.append((high[i] * 0.997, high[i]))

    # cluster zones
    def cluster(zones):
        if not zones:
            return []
        zones = sorted(zones)
        merged = [zones[0]]
        for z in zones[1:]:
            last = merged[-1]
            if abs(z[0] - last[1]) / last[1] < 0.004:
                merged[-1] = (min(last[0], z[0]), max(last[1], z[1]))
            else:
                merged.append(z)
        return merged

    return cluster(zones_demand), cluster(zones_supply)


def auto_reversal_alert(prob, direction):
    """
    Hanya trigger alert ketika crossing threshold.
    """
    if "rev_last_direction" not in st.session_state:
        st.session_state.rev_last_direction = None

    last = st.session_state.rev_last_direction
    alert_msg = None

    # Threshold
    UP_TH = 65
    DN_TH = 35

    if direction == "UP" and prob >= UP_TH and last != "UP":
        alert_msg = f"🟢 **Reversal Signal: STRONG BUY (prob {prob}%)**"
        st.session_state.rev_last_direction = "UP"

    elif direction == "DOWN" and prob <= DN_TH and last != "DOWN":
        alert_msg = f"🔴 **Reversal Signal: STRONG SELL (prob {prob}%)**"
        st.session_state.rev_last_direction = "DOWN"

    return alert_msg

def render_reversal_premium_level2(df):
    from components.reversal_premium import premium_reversal

    st.markdown("## 🔮 Premium Reversal Engine — Level 2")

    # -----------------------------------
    # RUN engine
    # -----------------------------------
    prob, direction, conf, expl = premium_reversal(df)

    # Simpan history
    add_history(prob)
    hist = get_memory()

    # -----------------------------------
    # AUTO ALERT SECTION
    # -----------------------------------
    alert = auto_reversal_alert(prob, direction)
    if alert:
        st.markdown(f"""
        <div style="
            padding:18px;
            background: rgba(255,255,255,0.1);
            border-radius:12px;
            border:1px solid rgba(255,255,255,0.2);
            box-shadow:0 0 15px rgba(0,255,0,0.6);
            font-size:18px;
            font-weight:600;
        ">
            {alert}
        </div>
        """, unsafe_allow_html=True)

    # -----------------------------------
    # PREMIUM CARD DISPLAY
    # -----------------------------------
    col = "🟢" if direction=="UP" else "🔴" if direction=="DOWN" else "⚪"

    st.markdown(f"""
        ### {col} {direction} — {prob}%  
        Confidence: **{conf*100:.1f}%**
    """)

    # -----------------------------------
    # CONFIDENCE HISTORY CHART
    # -----------------------------------
    st.markdown("### 📈 Reversal Confidence History (Live)")

    if len(hist) > 2:
        st.line_chart(hist)
    else:
        st.info("Reversal history not enough. Wait 2–3 refresh cycles.")

    # -----------------------------------
    # ZONES
    # -----------------------------------
    st.markdown("### 🧭 Reversal Zones (Demand & Supply)")

    demand, supply = detect_zones(df)

    st.markdown("#### 🟢 Demand Zones")
    if demand:
        for d in demand:
            st.markdown(f"- **{d[0]:.2f} → {d[1]:.2f}**")
    else:
        st.markdown("- No demand zones detected")

    st.markdown("#### 🔴 Supply Zones")
    if supply:
        for s in supply:
            st.markdown(f"- **{s[0]:.2f} → {s[1]:.2f}**")
    else:
        st.markdown("- No supply zones detected")

    # -----------------------------------
    # EXPLANATIONS
    # -----------------------------------
    st.markdown("### 📘 Reasoning")
    for e in expl:
        st.markdown(f"- {e}")

    st.markdown("---")
