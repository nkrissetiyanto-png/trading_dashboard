import streamlit as st

def render_battle_meter(score: int = 50):
    """
    score = 0–100
    0   → Foreign heavy SELL (dominan lokal)
    50  → Balanced
    100 → Foreign heavy BUY
    """
    # Clamp skor supaya selalu 0–100
    try:
        score = int(score)
    except Exception:
        score = 50

    score = max(0, min(score, 100))
    width_pct = score

    # Label status
    if score >= 70:
        label = "🟢 Foreign Accumulation — asing agresif beli"
    elif score <= 30:
        label = "🔴 Foreign Distribution — asing agresif jual"
    else:
        label = "⚪ Balanced Flow — tarik menarik lokal vs asing"

    # Side text (domestic vs foreign)
    if score > 55:
        side = "Kekuatan asing sedikit lebih dominan."
    elif score < 45:
        side = "Tekanan jual asing lebih besar, waspada koreksi."
    else:
        side = "Kekuatan lokal dan asing relatif seimbang."

    # ==== CSS PREMIUM (ANIMATED + GLOW) ====
    st.markdown(
        """
        <style>
        .df-card {
            padding:18px 22px;
            border-radius:18px;
            background:radial-gradient(circle at top, #111827 0, #020617 55%);
            border:1px solid rgba(148,163,184,0.35);
            box-shadow:0 0 0 1px rgba(15,23,42,0.8), 0 18px 45px rgba(0,0,0,0.75);
            margin-top:10px;
        }
        .df-title {
            font-size:15px;
            font-weight:600;
            color:#e5e7eb;
            margin-bottom:10px;
        }
        .df-bar-outer {
            width:100%;
            height:18px;
            border-radius:999px;
            background:linear-gradient(90deg,#020617,#020617);
            overflow:hidden;
            border:1px solid rgba(51,65,85,0.9);
            position:relative;
        }
        .df-bar-inner {
            height:100%;
            border-radius:999px;
            background:linear-gradient(90deg,#ef4444,#f97316,#eab308,#22c55e);
            box-shadow:0 0 18px rgba(34,197,94,0.6);
            animation:dfGlow 2.4s ease-in-out infinite;
            transform-origin:left center;
        }
        @keyframes dfGlow {
            0%   { box-shadow:0 0 10px rgba(34,197,94,0.35); }
            50%  { box-shadow:0 0 26px rgba(34,197,94,0.95); }
            100% { box-shadow:0 0 10px rgba(34,197,94,0.35); }
        }
        .df-footer {
            margin-top:10px;
            font-size:13px;
            color:#d1d5db;
        }
        .df-footer span.df-score {
            font-weight:700;
            color:#facc15;
        }
        .df-sub {
            font-size:12px;
            color:#9ca3af;
            margin-top:4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ==== HTML KOMPONEN ====
    html = f"""
    <div class="df-card">
        <div class="df-title">
            ⚔️ Domestic vs Foreign Battle Meter (Premium)
        </div>

        <div class="df-bar-outer">
            <div class="df-bar-inner" style="width:{width_pct}%;"></div>
        </div>

        <div class="df-footer">
            Score: <span class="df-score">{score}/100</span><br/>
            {label}
            <div class="df-sub">
                {side}
            </div>
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)
