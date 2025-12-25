import streamlit as st
import hashlib

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

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def login_ui():
    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = USERS.get(username)

        if not user:
            st.error("User tidak ditemukan")
            return False

        if password != user["password"]:
            st.error("Password salah")
            return False

        # SIMPAN SESSION
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = user["role"]

        st.success(f"Login berhasil sebagai {user['role']}")
        st.rerun()

    return False

def is_premium():
    return st.session_state.get("role") == "PREMIUM"
