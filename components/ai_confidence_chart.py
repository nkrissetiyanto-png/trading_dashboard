# components/ai_confidence_chart.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from components.ai_memory import get_history

def render_ai_confidence_chart():
    
    history = get_history()
    if len(history) < 3:
        st.info("AI confidence history belum cukup untuk ditampilkan.")
        return
    
    df = pd.DataFrame(history)
    df["t"] = pd.to_datetime(df["time"], unit="s")
    
    fig = go.Figure()

    # Line confidence
    fig.add_trace(go.Scatter(
        x=df["t"],
        y=df["confidence"],
        mode="lines+markers",
        line=dict(width=2, color="white"),
        marker=dict(size=6),
        name="Confidence"
    ))

    # Horizontal bands (optional aesthetic)
    fig.update_yaxes(range=[0, 1])

    fig.update_layout(
        template="plotly_dark",
        height=240,
        title="📊 AI Confidence Trend",
        margin=dict(l=10, r=10, t=30, b=10),
    )

    st.write("History size:", len(history))
    st.plotly_chart(fig, use_container_width=True)
