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
    
# 🔒 Authentication check
if not st.session_state.get("logged_in"):
    st.switch_page("pages/Login.py")

def logout():
    for key in ["logged_in", "username", "is_admin", "name"]:
        st.session_state.pop(key, None)
    st.success("Logged out.")
    st.experimental_rerun()

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
            st.session_state.name = users[username].get("name", username)
            st.session_state.is_admin = users[username].get("role", "") == "admin"
            st.success("Logged in successfully!")

            # Redirect after login using page names, not file paths
            if st.session_state.is_admin:
                st.switch_page("Admin.py")
            else:
                st.switch_page("Home.py")
        else:
            st.error("Invalid username or password")

# Sidebar UI: show Login or Logout button dynamically
st.sidebar.markdown("### Account")
if st.session_state.logged_in:
    if st.sidebar.button("🔓 Log Out"):
        logout()
else:
    # Show login button only if not logged in
    if st.sidebar.button("🔐 Login"):
        # Show login form on main page only
        login()

# When logged in, redirect away from this blank page to proper app page
if st.session_state.logged_in:
    if st.session_state.is_admin:
        st.experimental_set_query_params()  # clear params to prevent loops
        st.switch_page("pages/Admin.py")
    else:
        st.experimental_set_query_params()
        st.switch_page("pages/Home.py")

# If not logged in and sidebar login button not pressed, just stay blank here
