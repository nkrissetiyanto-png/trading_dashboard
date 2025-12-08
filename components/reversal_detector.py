import streamlit as st
from components.ai_reversal import detect_reversal

def render_reversal_detector(df, sensitivity):
    st.markdown("## 🔄 AI Reversal Detector")

    signal, explanations = detect_reversal(df, sensitivity)

    if signal is None:
        st.info("No clear reversal signal detected.")
    else:
        color = "🟢" if signal == "UP" else "🔴"
        st.markdown(f"### {color} Reversal Detected: **{signal}**")

    st.markdown("### Explanation:")
    for e in explanations:
        st.markdown(f"- {e}")
