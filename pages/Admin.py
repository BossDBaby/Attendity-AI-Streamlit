import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(page_title="Admin Panel - Attendity")

if not st.session_state.get('is_admin'):
    st.error("You are not authorized to view this page.")
    st.stop()

st.sidebar.page_link("app.py", label="Log Out")
st.sidebar.page_link("pages/1_Home.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/2_Attendance.py", label="Attendance", icon="🧍")
st.sidebar.page_link("pages/3_History.py", label="History", icon="📊")
st.sidebar.page_link("pages/4_Admin.py", label="Admin Panel", icon="🛠")

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
                users = []

            if any(user["username"] == new_username for user in users):
                st.error("Username already exists.")
            else:
                users.append({
                    "username": new_username,
                    "password": new_password,
                    "name": new_name,
                    "email": new_email,
                    "role": "student"
                })

                with open("data/users.json", "w") as f:
                    json.dump(users, f, indent=4)

                st.success(f"Student '{new_username}' added successfully.")

                st.info("📷 Please upload a facial photo for this student to `assets/user_photos/` with filename: **" + new_username + ".jpg**")

