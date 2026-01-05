import time
import streamlit as st

from components.chart import render_chart
from components.indicators import render_indicators
from components.orderbook import render_orderbook
from components.smartmoney import render_smartmoney
from components.signals import render_signals
from components.sentiment import render_sentiment
from components.crypto_sentiment import render_crypto_sentiment
from components.ai_signal import render_ai_signal
from data.data_loader import load_candles
from components.ai_confidence_chart import render_ai_confidence_chart
from components.ai_final_engine import final_decision_engine
from components.reversal_detector import render_reversal_detector
from components.ai_predictor import AIPredictor
from components.indo_heatmap import render_heatmap
from components.indo_battle_meter import render_battle_meter
from components.reversal_premium_ui import render_reversal_premium
from components.reversal_premium_level2 import render_reversal_premium_level2
from auth import login_ui, is_premium, logout, init_auth, check_timeout, is_guest
from db import init_db

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="🔥 Cuanmology Trading Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()
init_auth()
check_timeout()

if st.session_state.logged_in:
    st.session_state.show_login = False

#if not is_guest():
#    if st.sidebar.button("🚪 Logout"):
#        logout()
#else:
#    st.sidebar.info("🔓 Mode Demo")
#    if st.sidebar.button("🔐 Login / Join"):
#        st.session_state.show_login = True



#st.sidebar.markdown("🔐 **Mode Demo**")

if st.session_state.plan == "GUEST":
    if st.sidebar.button("👀 Mode Demo"):
        st.session_state.show_login = False
        st.rerun()

    if st.sidebar.button("🔐 Login / Join"):
        st.session_state.show_login = True
        st.rerun()
else:
    #st.sidebar.markdown(f"👤 {st.session_state.username}")
    #st.sidebar.caption(f"Plan: {st.session_state.plan}")

    if st.sidebar.button("🚪 Logout"):
        logout()
        
# =========================
# OPTIONAL LOGIN MODAL
# =========================
#if st.session_state.get("show_login"):
#    login_ui()
#    st.stop()
    
if st.session_state.get("show_login", False) and not st.session_state.logged_in:
    login_ui()
    st.stop()
    
#if "logged_in" not in st.session_state:
#    st.session_state.logged_in = False

#if not st.session_state.logged_in:
#    login_ui()
#    st.stop()
    

# ================================
# GOOGLE ANALYTICS (GLOBAL SCRIPT)
# ================================
GA_ID = "G-4RD8K3ZQ52"

st.markdown(f"""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', '{GA_ID}');
</script>
""", unsafe_allow_html=True)

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

ai = AIPredictor()

def premium_loading():
    """Overlay loading premium."""
    st.markdown("""
    <div class="loader-overlay">
        <div class="premium-loader"></div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown(
    f"""
    👤 **User:** {st.session_state.username}  
    ⭐ **Plan:** {st.session_state.plan}
    """
)

def news_ticker():
    st.markdown("""
    <style>
    .ticker {
        background: linear-gradient(90deg,#1f2937,#111827);
        color: #fbbf24;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 0.9rem;
        animation: pulse 2.5s infinite;
    }
    @keyframes pulse {
        0% {opacity: 0.6;}
        50% {opacity: 1;}
        100% {opacity: 0.6;}
    }
    </style>

    <div class="ticker">
    🚀 Join membership untuk insight lebih lengkap, AI signal, dan multi-timeframe analysis
    </div>
    """, unsafe_allow_html=True)

def teaser(msg="Upgrade untuk membuka fitur ini"):
    st.info(f"🔒 {msg}")
    
if st.session_state.plan in ["GUEST", "FREE"]:
    news_ticker()
    
#st.sidebar.success(f"👋 {st.session_state.username}")
#st.sidebar.caption(f"Role: {st.session_state.role}")

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

reversal_sensitivity = st.sidebar.select_slider(
    "Reversal Sensitivity",
    options=["Low", "Medium", "High"],
    value="Medium"
)

auto_refresh = st.sidebar.checkbox("Auto Refresh", True)
refresh_rate = st.sidebar.slider("Refresh (seconds)", 3, 30, 5)

#st.sidebar.markdown("---")
#if st.sidebar.button("🚪 Logout"):
#    logout()
#    st.rerun()  

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

        st.title(f"🔥 Cuanmology Trading Dashboard — {symbol}")

        col1, col2 = st.columns([3, 1])

        with col1:
            render_smartmoney(df)
            render_chart(df)
            render_indicators(df)

            if is_premium():
                if mode.startswith("Saham Indonesia"):
                    render_sentiment(symbol)
                    render_heatmap(df)
                    render_battle_meter()
                    render_reversal_premium(df)
                    render_reversal_premium_level2(df)
                else:
                    render_crypto_sentiment(symbol)
                    render_ai_signal(df)
            
                    trend_result = ai.predict(df)
                    decision, reason, reversal_sig, smart_money = final_decision_engine(df, trend_result)
                    
                    st.markdown("## 🧠 AI Final Decision Engine")
                    
                    color = "🟢" if decision in ["BUY", "REVERSAL BUY"] else ("🔴" if decision in ["SELL", "TAKE PROFIT"] else "⚪")
                    
                    st.markdown(f"### {color} Final Decision: **{decision}**")
                    
                    st.markdown("### Reasoning:")
                    for r in reason:
                        st.markdown(f"- {r}")
    
                    render_reversal_detector(df, reversal_sensitivity)
                    render_ai_confidence_chart()
            else:
                teaser("AI Signal tersedia untuk member PREMIUM")
#                st.info("🔒 AI Confidence hanya untuk Premium")
                
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
