import streamlit as st
import pandas as pd
import os
import json
from utils.auth import hash_password

st.set_page_config(page_title="Admin Panel - Attendity")

# 🔒 Protect the page
if not st.session_state.get("logged_in") or not st.session_state.get("is_admin"):
    st.switch_page("pages/Login.py")

# 🚪 Logout button
st.sidebar.markdown("### Account")
st.sidebar.button("🔓 Log Out", on_click=lambda: [st.session_state.clear(), st.rerun()])

# 🧭 Navigation
st.sidebar.page_link("pages/Home.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/History.py", label="History", icon="📊")
st.sidebar.divider()
st.sidebar.markdown("### Admin Section")
st.sidebar.page_link("pages/Admin.py", label="Admin Panel", icon="🛠")

# 🛠 Admin content
st.title("🛠 Admin Panel")

# === 📋 View Attendance Data ===
ATTENDANCE_FILE = "data/attendance.csv"

if os.path.exists(ATTENDANCE_FILE):
    df = pd.read_csv(ATTENDANCE_FILE)
    st.subheader("📋 Attendance Records")
    st.dataframe(df)

    if st.button("⚠️ Clear All Records"):
        os.remove(ATTENDANCE_FILE)
        st.success("All attendance records have been deleted.")
else:
    st.info("No attendance records found yet.")

st.markdown("---")

# === ➕ Add New Student ===
st.subheader("➕ Add New Student")

with st.form("add_student_form"):
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    new_name = st.text_input("Full Name")
    new_email = st.text_input("Email")
    submitted = st.form_submit_button("Add Student")

    if submitted:
        if not new_username or not new_password or not new_name or not new_email:
            st.warning("Please fill out all fields.")
        else:
            try:
                with open("data/users.json", "r") as f:
                    users = json.load(f)
            except FileNotFoundError:
                users = {}

            if new_username in users:
                st.error("Username already exists.")
            else:
                users[new_username] = {
                    "password": hash_password(new_password),
                    "name": new_name,
                    "email": new_email,
                    "role": "student"
                }

                with open("data/users.json", "w") as f:
                    json.dump(users, f, indent=4)

                st.success(f"Student '{new_username}' added successfully.")
                st.info("📷 Please upload a facial photo to `assets/user_photos/` named: **{new_username}.jpg**")
