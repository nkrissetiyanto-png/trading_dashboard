import streamlit as st
import hashlib
import time
from db import get_db

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
        "last_active": None,
        "show_login": False,
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
#def login_ui():
#    st.markdown("## 🔐 Login")

#    user = st.text_input("Username")
#    pw = st.text_input("Password", type="password")

#    if st.button("Login", use_container_width=True):
#        data = USERS.get(user)

#        if not data:
#            st.error("User tidak ditemukan")
#        elif hash_pw(pw) != data["password"]:
#            st.error("Password salah")
#        else:
#            st.session_state.logged_in = True
#            st.session_state.username = user
#            st.session_state.plan = data["plan"]
#            st.session_state.show_login = False
#            st.session_state.last_active = time.time()
#            st.rerun()

def login_ui():
    st.markdown("## 🔐 Login")

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login", use_container_width=True):
        data = USERS.get(username)

        if not data:
            st.error("User tidak ditemukan")
        elif hash_pw(password) != data["password"]:
            st.error("Password salah")
        else:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.plan = data["plan"]
            st.session_state.last_active = time.time()
            st.session_state.show_login = False

            # Clear input setelah sukses
            st.session_state.pop("login_user", None)
            st.session_state.pop("login_pass", None)

            st.rerun()

def register_user(username, password):
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, password_hash, plan, datejoin, lastpayment) VALUES (?, ?, ?, ?, ?)",
            (username, hash_pw(password), "FREE", "-","-")
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def authenticate(username, password):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT password_hash, plan FROM users WHERE username = ?",
        (username,)
    )
    row = c.fetchone()
    conn.close()

    if not row:
        return None

    if hash_pw(password) == row[0]:
        return row[1]  # plan
    return None

def login_ui_db():
    st.subheader("🔐 Login")

    u = st.text_input("Username", key="login_user")
    p = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        plan = authenticate(u, p)
        if not plan:
            st.error("Login gagal")
        else:
            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.plan = plan
            st.session_state.show_login = False
            st.rerun()

def register_ui():
    st.subheader("🆕 Register")

    u = st.text_input("Username", key="reg_user")
    p = st.text_input("Password", type="password", key="reg_pass")

    if st.button("Register"):
        if register_user(u, p):
            st.success("Akun dibuat. Silakan login.")
        else:
            st.error("Username sudah dipakai")

# =========================
# LOGOUT
# =========================
#def logout():
#    for k in list(st.session_state.keys()):
#        del st.session_state[k]
#    st.rerun()

def logout():
    # Reset ke mode demo
    st.session_state.logged_in = False
    st.session_state.username = "Guest"
    st.session_state.plan = "GUEST"
    st.session_state.last_active = None
    st.session_state.show_login = False

    # Reset input login
    st.session_state.pop("login_user", None)
    st.session_state.pop("login_pass", None)

    st.rerun()


# =========================
# PLAN CHECK
# =========================
def is_premium():
    return st.session_state.get("plan") == "PREMIUM"

def is_guest():
    return not st.session_state.get("logged_in", False)
