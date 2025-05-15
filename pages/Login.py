import streamlit as st
from utils.auth import login_user, load_users

st.set_page_config(page_title="Login | Attendity", layout="centered")

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

            # Redirect based on role
            if st.session_state.is_admin:
                st.switch_page("pages/Admin.py")
            else:
                st.switch_page("pages/Home.py")
        else:
            st.error("Invalid username or password")

# Run the login page logic
login()
