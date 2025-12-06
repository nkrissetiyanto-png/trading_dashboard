from components.ai_predictor import AIPredictor
import streamlit as st

ai = AIPredictor()

def render_ai_signal(df):

    result = ai.predict(df)

    direction = result["direction"]
    up = result["prob_up"]
    down = result["prob_down"]
    conf = result["confidence"]

    color = "🟢" if direction == "UP" else "🔴"

    st.markdown("## 🔮 AI Price Prediction (15m)")
    st.markdown(f"### {color} Predicted Direction: **{direction}**")
    st.markdown(f"**Prob UP:** {up:.2%}  —  **Prob DOWN:** {down:.2%}")
    st.markdown(f"**Confidence:** {conf:.2%}")
