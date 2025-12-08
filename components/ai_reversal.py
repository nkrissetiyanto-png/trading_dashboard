import streamlit as st
from components.ai_predictor import AIPredictor

ai = AIPredictor()

def render_ai_reversal(df):
    st.subheader("🔄 AI Reversal Detector")

    result = ai.detect_reversal(df)

    if result["type"] is None:
        st.info("No clear reversal signal detected.")
        return

    t = result["type"]
    score = result["score"]
    reasons = result["reasons"]

    color = "🟢" if t == "bullish" else "🔴"
    label = "Bullish Reversal" if t == "bullish" else "Bearish Reversal"

    st.markdown(f"""
        ### {color} **{label} Detected**  
        **Probability:** {score*100:.1f}%
    """)

    st.markdown("### Why?")
    for r in reasons:
        st.markdown(f"- {r}")

    st.markdown("---")
