import streamlit as st
import hashlib
import time

SESSION_TIMEOUT = 30 * 60  # 30 menit

# =========================
# USER DATABASE (contoh)
# =========================
USERS = {
    "demo": {
        "password": hashlib.sha256("demo123".encode()).hexdigest(),
        "plan": "FREE"
    },
    "nanang": {
        "password": hashlib.sha256("premium123".encode()).hexdigest(),
        "plan": "PREMIUM"
    }
}

# =========================
# INIT SESSION
# =========================
#def init_auth():
#    defaults = {
#        "logged_in": False,
#        "username": None,
#        "plan": None,
#        "last_active": None
#    }
#    for k, v in defaults.items():
#        if k not in st.session_state:
#            st.session_state[k] = v
            
def init_auth():
    defaults = {
        "logged_in": False,
        "username": "Guest",
        "plan": "GUEST",
        "last_active": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# =========================
# HASH
# =========================
def hash_pw(pw: str):
    return hashlib.sha256(pw.encode()).hexdigest()

# =========================
# SESSION CHECK
# =========================
def check_timeout():
    if st.session_state.logged_in:
        now = time.time()
        if st.session_state.last_active and now - st.session_state.last_active > SESSION_TIMEOUT:
            logout()
        else:
            st.session_state.last_active = now

# =========================
# LOGIN UI
# =========================
def login_ui():
    st.markdown("## 🔐 Login")

    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        data = USERS.get(user)

        if not data:
            st.error("User tidak ditemukan")
        elif hash_pw(pw) != data["password"]:
            st.error("Password salah")
        else:
            st.session_state.logged_in = True
            st.session_state.username = user
            st.session_state.plan = data["plan"]
            st.session_state.last_active = time.time()
            st.rerun()

# =========================
# LOGOUT
# =========================
def logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# =========================
# PLAN CHECK
# =========================
def is_premium():
    return st.session_state.get("plan") == "PREMIUM"

def is_guest():
    return not st.session_state.get("logged_in", False)
