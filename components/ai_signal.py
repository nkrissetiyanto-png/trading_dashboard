import streamlit as st
from components.ai_predictor import AIPredictor

ai = AIPredictor()

# ======================== PREMIUM CSS ========================
AI_CSS = """
<style>
.ai-card {
    padding:20px;
    border-radius:20px;
    background:rgba(255,255,255,0.07);
    border:1px solid rgba(255,255,255,0.18);
    backdrop-filter: blur(12px);
    box-shadow:0 6px 20px rgba(0,0,0,0.35);
    text-align:center;
    margin-top:15px;
}
.ai-title {
    font-size:18px;
    color:#E5ECF5;
    font-weight:600;
}
.ai-value {
    font-size:36px;
    font-weight:800;
    margin-top:4px;
}
.ai-sub {
    font-size:14px;
    color:#AAB4C2;
    margin-top:6px;
}
</style>
"""

def render_ai_signal(df):

    st.markdown(AI_CSS, unsafe_allow_html=True)

    direction, prob = ai.predict_direction(df)

    pct = round(prob * 100, 2)

    # Determine colors & emojis
    if direction == "UP":
        emoji = "🚀"
        color = "linear-gradient(90deg, #2ecc71, #27ae60)"
    else:
        emoji = "📉"
        color = "linear-gradient(90deg, #e74c3c, #c0392b)"

    # Simple AI explanation (auto)
    if direction == "UP":
        explanation = (
            "Model mendeteksi momentum bullish, volume positif, dan sinyal MACD "
            "yang cenderung menguat. Probabilitas harga naik cukup tinggi."
        )
    else:
        explanation = (
            "Model melihat tekanan jual meningkat, momentum melemah, dan pola candle "
            "cenderung bearish. Risiko penurunan lebih dominan."
        )

    st.markdown(f"""
        <div class="ai-card">
            <div class="ai-title">{emoji} AI Prediction</div>
            <div class="ai-value" style="background:{color};
                 -webkit-background-clip:text; color:transparent;">
                {direction}
            </div>
            <div class="ai-sub">Confidence: <b>{pct}%</b></div>
            <div class="ai-sub">{explanation}</div>
        </div>
    """, unsafe_allow_html=True)
