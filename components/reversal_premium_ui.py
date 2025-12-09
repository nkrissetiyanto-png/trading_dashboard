import streamlit as st
from components.reversal_premium import premium_reversal

def render_reversal_premium(df):
    st.markdown("## 🔮 Premium Reversal Probability")

    prob, direction, conf, expl = premium_reversal(df)

    color = "🟢" if direction=="UP" else "🔴" if direction=="DOWN" else "⚪"

    # ==========================
    # PREMIUM METER ANIMATION
    # ==========================
    meter_color = (
        "rgba(46, 204, 113,0.85)" if direction=="UP"
        else "rgba(231,76,60,0.85)" if direction=="DOWN"
        else "rgba(255,255,255,0.25)"
    )

    st.markdown(f"""
    <div style="
        margin:15px 0;
        padding:25px;
        border-radius:18px;
        background:rgba(255,255,255,0.05);
        backdrop-filter:blur(8px);
        border:1px solid rgba(255,255,255,0.15);
        box-shadow:0 0 25px {meter_color};
        text-align:center;
        animation: glow 3s infinite alternate;
    ">
        <h2 style="color:white; margin-bottom:5px;">{color} {direction}</h2>
        <div style="font-size:32px; font-weight:700; color:white;">
            {prob}%
        </div>
        <p style="color:#AAB4C2; margin-top:6px;">
            Confidence: {conf*100:.1f}%
        </p>
    </div>

    <style>
    @keyframes glow {{
        from {{ box-shadow:0 0 10px {meter_color}; }}
        to   {{ box-shadow:0 0 30px {meter_color}; }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # ==========================
    # EXPLANATIONS
    # ==========================
    st.markdown("### 📘 Explanation")

    for e in expl:
        st.markdown(f"- {e}")

    st.markdown("---")
