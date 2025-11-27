import plotly.graph_objects as go
import streamlit as st

def render_chart(df):
    st.subheader("📈 Candlestick Chart")

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name="Market Data"
    ))

    fig.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_rangeslider_visible=False,
        margin=dict(l=5, r=5, t=30, b=5)
    )

    st.plotly_chart(fig, use_container_width=True)
