import streamlit as st
import requests

def render_orderbook(symbol):
    st.subheader("📚 Orderbook")

    url = f"https://api.mexc.com/api/v3/depth?symbol={symbol}&limit=20"
    data = requests.get(url).json()

    bids = data["bids"]
    asks = data["asks"]

    st.write("**BIDS**")
    st.dataframe(bids)

    st.write("**ASKS**")
    st.dataframe(asks)
