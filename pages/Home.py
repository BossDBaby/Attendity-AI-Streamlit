import streamlit as st
import pandas as pd
from streamlit_extras.stylable_container import stylable_container

# 🛠 Page config
st.set_page_config(page_title="Home - Attendity", layout="centered")

# 🔒 Authentication check
if not st.session_state.get("logged_in"):
    st.switch_page("pages/Login.py")

# 🚪 Logout button
st.sidebar.markdown("### Account")
st.sidebar.button("🔓 Log Out", on_click=lambda: [st.session_state.clear(), st.rerun()])
st.sidebar.page_link("pages/Home.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/History.py", label="History", icon="📊")

# 🛠 Admin tools (only if admin)
if st.session_state.get("is_admin"):
    st.sidebar.divider()
    st.sidebar.markdown("### Admin Section")
    st.sidebar.page_link("pages/Admin.py", label="Admin Panel", icon="🛠")

# 👋 Welcome user
full_name = st.session_state.get("name", st.session_state.get("username", "User"))
st.title(f"Hi, {full_name} 👋")
st.subheader("Welcome to your Class Dashboard")

# 📅 Dummy class schedule
subjects = [
    ("UI-UX", "09:30 AM"),
    ("Project", "10:40 AM"),
    ("AI", "11:45 AM"),
    ("Cyber Security", "12:10 PM"),
    ("Ethical Hacking", "12:45 PM"),
    ("Software Engineering", "13:30 PM")
]

# 📘 Styled Subject Table
st.markdown("### 📘 Today's Schedule")

for subject, time in subjects:
    with stylable_container(
        key=subject,
        css_styles="""
            button {
                width: 100%;
                padding: 1rem;
                margin-bottom: 0.5rem;
                border-radius: 0.5rem;
                border: 1px solid #ccc;
                background-color: #0e1321;
                font-size: 1rem;
                transition: 0.2s all ease-in-out;
            }
            button:hover {
                background-color: #090c14;
                cursor: pointer;
            }
        """
    ):
        if st.button(f"📘 {subject} ({time})", key=f"btn_{subject}"):
            st.session_state["selected_subject"] = subject
            st.switch_page("pages/Attendance.py")
