import plotly.graph_objects as go
import streamlit as st

def render_chart(df):
    st.subheader("📈 Candlestick Chart")

    fig = go.Figure(data=[
        go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name="Market Data"
        )
    ])

    fig.update_layout(
        template="plotly_dark",
        height=450,
        margin=dict(l=10, r=10, t=30, b=10),
    )

    st.plotly_chart(fig, use_container_width=True)
