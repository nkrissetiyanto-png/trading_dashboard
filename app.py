import time
import streamlit as st
import subprocess

from components.chart import render_chart
from components.indicators import render_indicators
from components.orderbook import render_orderbook
from components.smartmoney import render_smartmoney
from components.signals import render_signals
from components.sentiment import render_sentiment
from components.crypto_sentiment import render_crypto_sentiment
#from components.ai_signal import render_ai_signal
from data.data_loader import load_candles


# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="🔥 Nanang Trading Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================
# PREMIUM LOADING CSS
# ======================================================
st.markdown("""
<style>

.loader-overlay {
    position: fixed;
    top:0; left:0;
    width:100vw;
    height:100vh;
    background: rgba(0,0,0,0.55);
    backdrop-filter: blur(6px);
    display:flex;
    justify-content:center;
    align-items:center;
    z-index:9999;
}

.premium-loader {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    border: 6px solid rgba(255,255,255,0.25);
    border-top-color: #16e06f;
    animation: spin 1.1s linear infinite;
    box-shadow: 0 0 25px #16e06f;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

</style>
""", unsafe_allow_html=True)


def premium_loading():
    """Overlay loading premium."""
    st.markdown("""
    <div class="loader-overlay">
        <div class="premium-loader"></div>
    </div>
    """, unsafe_allow_html=True)


# ======================================================
# SIDEBAR SETTINGS
# ======================================================
st.sidebar.title("⚙️ Settings")

mode = st.sidebar.selectbox(
    "Market",
    ["Crypto (MEXC — Recommended)", "Saham Indonesia"]
)

symbol = st.sidebar.text_input(
    "Symbol",
    "BTCUSDT" if mode.startswith("Crypto") else "BBNI.JK"
)

intervals_crypto = ["1m", "5m", "15m", "1h", "1d"]
intervals_stock = ["5m", "15m", "1h", "1d"]

interval = st.sidebar.selectbox(
    "Interval",
    intervals_stock if mode.startswith("Saham") else intervals_crypto
)

auto_refresh = st.sidebar.checkbox("Auto Refresh", True)
refresh_rate = st.sidebar.slider("Refresh (seconds)", 3, 30, 5)

if st.sidebar.button("Train Model"):
    st.sidebar.write("Training dimulai...")

    #process = subprocess.Popen(
    #    ["python", "ai/train_crypto_ai.py"], 
    #    stdout=subprocess.PIPE, 
    #    stderr=subprocess.STDOUT,
    #    text=True
    #)
    process = subprocess.Popen(
        ["pip install", "pandas"], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        text=True
    )

    log_area = st.empty()
    log_text = ""

    for line in process.stdout:
        log_text += line
        log_area.text(log_text)

    process.wait()
    st.sidebar.success("Training selesai!")

# ======================================================
# MAIN PAGE CONTAINER (ANTI FLICKER)
# ======================================================
page = st.empty()


# ======================================================
# DASHBOARD LOOP
# ======================================================
while True:

    # --- tampilkan loading overlay ---
    loading_area = st.empty()
    with loading_area:
        premium_loading()

    # --- load data ---
    try:
        df = load_candles(symbol, interval, mode)
    except Exception as e:
        loading_area.empty()
        st.error(f"❌ Gagal memuat data: {e}")
        st.stop()

    # --- hilangkan loader setelah data siap ---
    loading_area.empty()

    # --- render semua konten di container stabil ---
    with page.container():

        st.title(f"🔥 Nanang Premium Dashboard — {symbol}")

        col1, col2 = st.columns([3, 1])

        with col1:
            render_chart(df)
            render_indicators(df)
            render_smartmoney(df)

            if mode.startswith("Saham Indonesia"):
                render_sentiment(symbol)
            else:
                render_crypto_sentiment()

            #render_ai_signal(df)
            render_signals(df)

        with col2:
            if mode.startswith("Crypto"):
                render_orderbook(symbol)
            else:
                st.info("Orderbook tidak tersedia untuk saham Indo.")

    # --- kontrol auto refresh ---
    if not auto_refresh:
        break

    time.sleep(refresh_rate)
    st.rerun()    # ⬅️ ganti ke st.rerun, bukan experimental_rerun
