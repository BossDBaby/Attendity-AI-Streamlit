import streamlit as st
from sqlalchemy.orm import Session
from config.database import db_manager
from models.attendance_models import User
import bcrypt

st.set_page_config(page_title="Login | Attendity", layout="centered")

def get_user_by_username(session: Session, username: str):
    """Fetch a user by username from the database."""
    return session.query(User).filter(User.username == username).first()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored hashed password."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def login():
    st.title("Attendity")
    st.subheader("LOGIN TO YOUR ACCOUNT")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    remember_me = st.checkbox("Remember me", value=True)

    if st.button("LOG IN"):
        with db_manager.get_session() as session:
            user = get_user_by_username(session, username)

            if user and verify_password(password, user.password_hash):
                # Set session state
                st.session_state.logged_in = True
                st.session_state.username = user.username
                st.session_state.name = user.name
                st.session_state.is_admin = user.role == "admin"
                st.session_state.user_id = user.id
                st.session_state.role = user.role
                st.success("Logged in successfully!")

                # Redirect based on role
                if st.session_state.is_admin:
                    st.switch_page("pages/Admin.py")
                else:
                    st.switch_page("pages/Home.py")
            else:
                st.error("Invalid username or password")

# Run the login logic
login()
