import streamlit as st
from components.ai_predictor import AIPredictor

ai = AIPredictor()

def render_ai_signal(df):
    st.subheader("🔮 AI Price Prediction (15m)")
    #st.write("DEBUG — Data length:", len(df))

    result = ai.predict(df)
    if result is None:
        st.warning("AI model unavailable.")
        return

    direction = result["direction"]
    prob_up = result["prob_up"]
    prob_down = result["prob_down"]
    conf = result["confidence"]
    explanations = result.get("explanations", [])
    
    color = "🟢" if direction == "UP" else "🔴"

    st.markdown(f"""
        ### {color} Prediction: **{direction}**
        **Confidence:** {conf*100:.2f}%  
        **Up:** {prob_up*100:.2f}%  
        **Down:** {prob_down*100:.2f}%
    """)

    if direction == "UP" and conf > 0.3:
        st.success("Strong BUY signal")
    elif direction == "DOWN" and conf > 0.3:
        st.error("Strong SELL signal")
    else:
        st.info("Market uncertain — Scalping only.")

    # ============================================================
    # ================  AI EXPLANATION SECTION ====================
    # ============================================================

    st.markdown("### 📘 AI Explanation (Why this prediction?)")

    for msg in explanations:
        st.markdown(f"- {msg}")

    st.markdown("---")
