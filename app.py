import streamlit as st
from components.chart import render_chart
from components.orderbook import render_orderbook
from components.indicators import render_indicators
from components.smartmoney import render_smartmoney
from data.data_loader import load_candles

st.set_page_config(
    page_title="🔥 Nanang Trader Pro Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============== SIDEBAR ===============
st.sidebar.title("⚙️ Settings")
symbol = st.sidebar.text_input("Symbol", "BTCUSDT")
interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "1h"])
auto_refresh = st.sidebar.checkbox("Auto Refresh", True)
refresh_rate = st.sidebar.slider("Refresh (seconds)", 3, 30, 5)

st.sidebar.markdown("---")
st.sidebar.caption("Nanang Premium Trading Dashboard © 2025")

# =============== MAIN CONTENT ===============
st.title(f"🔥 Nanang Trading Dashboard — {symbol}")

df = load_candles(symbol, interval)

col1, col2 = st.columns([3, 1])

with col1:
    render_chart(df)
    render_indicators(df)
    render_smartmoney(df)

with col2:
    render_orderbook(symbol)

# Auto-refresh
if auto_refresh:
    st.experimental_rerun()
