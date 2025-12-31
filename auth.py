import streamlit as st

# =========================
# USER DATABASE (sementara)
# =========================
USERS = {
    "demo": {
        "password": "demo123",
        "role": "FREE"
    },
    "nanang": {
        "password": "premium123",
        "role": "PREMIUM"
    }
}

# =========================
# INIT SESSION STATE
# =========================
def init_auth():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "role" not in st.session_state:
        st.session_state.role = None

# =========================
# LOGIN UI
# =========================
def login_ui():
    st.markdown("## 🔐 Login")

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login", use_container_width=True):
        user = USERS.get(username)

        if not user:
            st.error("❌ User tidak ditemukan")
        elif password != user["password"]:
            st.error("❌ Password salah")
        else:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user["role"]
            st.rerun()

# =========================
# LOGOUT (FULL RESET)
# =========================
def logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# =========================
# ROLE CHECK
# =========================
def is_premium():
    return st.session_state.get("role") == "PREMIUM"
