import streamlit as st
from components.chart import render_chart
from components.indicators import render_indicators
from components.orderbook import render_orderbook
from components.smartmoney import render_smartmoney
from components.signals import render_signals
from data.data_loader import load_candles

st.set_page_config(
    page_title="🔥 Nanang Trading Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar settings
st.sidebar.title("⚙️ Settings")
mode = st.sidebar.selectbox("Market", ["Crypto (MEXC/Binance)", "Saham Indonesia"])

symbol = st.sidebar.text_input("Symbol", "BTCUSDT" if mode.startswith("Crypto") else "BBNI.JK")
#interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "1h", "1d"])

# INTERVAL HANDLING
if mode.startswith("Saham Indonesia"):
    valid_intervals = ["5m", "15m", "1h", "1d"]
else:
    valid_intervals = ["1m", "5m", "15m", "1h", "1d"]

interval = st.sidebar.selectbox("Interval", valid_intervals)


auto_refresh = st.sidebar.checkbox("Auto Refresh", True)
refresh_rate = st.sidebar.slider("Refresh (seconds)", 3, 30, 5)

# Load data
df = load_candles(symbol, interval, mode)

st.title(f"🔥 Nanang Premium Dashboard — {symbol}")

col1, col2 = st.columns([3, 1])

with col1:
    render_chart(df)
    render_indicators(df)
    render_smartmoney(df)
    render_signals(df)

with col2:
    if mode.startswith("Crypto"):
        render_orderbook(symbol)
    else:
        st.info("Orderbook tidak tersedia untuk saham Indo.")

if auto_refresh:
    st.experimental_rerun()
