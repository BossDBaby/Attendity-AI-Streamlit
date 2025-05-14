import streamlit as st
from utils.auth import login_user, load_users

st.set_page_config(page_title="Attendity", layout="centered")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "name" not in st.session_state:
    st.session_state.name = None

# Logout function
def logout():
    for key in ["logged_in", "username", "is_admin", "name"]:
        st.session_state.pop(key, None)
    st.success("Logged out.")
    st.rerun()

# Login form
def login():
    st.title("Attendity")
    st.subheader("LOGIN TO YOUR ACCOUNT")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    remember_me = st.checkbox("Remember me", value=True)

    if st.button("LOG IN"):
        users = load_users()
        if login_user(username, password, users):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.name = users[username].get("name", username)  # Store real name
            st.session_state.is_admin = users[username].get("role", "") == "admin"
            st.success("Logged in successfully!")

            # Redirect after login
            if st.session_state.is_admin:
                st.switch_page("admin/dashboard.py")
            else:
                st.switch_page("pages/Home.py")
        else:
            st.error("Invalid username or password")

# Sidebar logout button
st.sidebar.markdown("### Account")
if st.sidebar.button("🔓 Log Out"):
    logout()

# Auto redirect if already logged in
if not st.session_state.logged_in:
    login()
else:
    if st.session_state.is_admin:
        st.switch_page("admin/dashboard.py")
    else:
        st.switch_page("pages/Home.py")
