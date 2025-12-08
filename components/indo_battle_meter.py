import streamlit as st

def render_battle_meter(score: int = 50):
    """
    score = 0–100
    0  → Foreign Sell Heavy (dominan lokal)
    50 → Balanced
    100 → Foreign Buy Heavy
    """

    score = max(0, min(score, 100))
    width_pct = score  # 0–100

    # Label kondisi
    if score > 65:
        label = "🟢 Foreign Accumulating"
    elif score < 35:
        label = "🔴 Foreign Selling"
    else:
        label = "⚪ Balanced Flow"

    st.markdown("## ⚔️ Domestic vs Foreign Battle Meter (Premium)")

    html = f"""
    <div style="
        padding:20px;
        border-radius:16px;
        background:#0d1117;
        border:1px solid rgba(255,255,255,0.1);
        margin-top:10px;
    ">
        <div style="color:#e5e7eb; font-size:15px; margin-bottom:10px;">
            Foreign Strength Meter
        </div>

        <div style="
            width:100%;
            height:18px;
            border-radius:999px;
            background:#111827;
            overflow:hidden;
            border:1px solid rgba(55,65,81,0.9);
            position:relative;
        ">
            <div style="
                width:{width_pct}%;
                height:100%;
                background:linear-gradient(90deg,#ef4444,#f59e0b,#22c55e);
                transition:width 0.4s ease-out;
            "></div>
        </div>

        <div style="margin-top:10px; color:#d1d5db; font-size:13px;">
            Score: <b>{score}/100</b><br>
            {label}
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)
