import streamlit as st
import pandas as pd
import os
from glob import glob

st.set_page_config(page_title="History - Attendity")

# 🔒 Authentication check
if not st.session_state.get("logged_in"):
    st.switch_page("pages/Login.py")

# Sidebar Navigation
st.sidebar.markdown("### Account")
st.sidebar.button("🔓 Log Out", on_click=lambda: [st.session_state.clear(), st.experimental_rerun()])
st.sidebar.page_link("pages/Home.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/History.py", label="History", icon="📊")

# Admin section in sidebar if admin
if st.session_state.get("is_admin"):
    st.sidebar.divider()
    st.sidebar.markdown("### Admin Section")
    st.sidebar.page_link("pages/Admin.py", label="Admin Panel", icon="🛠")

st.title("📊 Your Attendance History")

username = st.session_state.get("username")
if not username:
    st.error("User not logged in.")
    st.stop()

attendance_folder = "assets/attendance"
all_files = glob(os.path.join(attendance_folder, "*.csv"))

if not all_files:
    st.info("No attendance records found yet.")
    st.stop()

# Map subject -> last attendance time for this user (if any)
attendance_summary = {}

for file in all_files:
    subject = os.path.splitext(os.path.basename(file))[0].replace('_', ' ').title()
    df = pd.read_csv(file)
    if 'Name' in df.columns and 'Time' in df.columns:
        user_records = df[df['Name'] == username]
        if not user_records.empty:
            last_time = pd.to_datetime(user_records['Time']).max()
            attendance_summary[subject] = last_time

st.markdown(f"### Student: **{username}**")
st.markdown("#### History")

all_subjects = [os.path.splitext(os.path.basename(f))[0].replace('_', ' ').title() for f in all_files]

for subject in sorted(all_subjects):
    last_time = attendance_summary.get(subject, None)
    time_str = last_time.strftime("%I:%M %p").lstrip('0') if last_time else "-"

    present = last_time is not None

    st.markdown(
        f"""
        <div style="
            border: 1px solid #ddd; 
            border-radius: 8px; 
            padding: 12px; 
            margin-bottom: 12px;
            background-color: #262730;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-weight: 600; font-size: 1.1em; color: inherit;">{subject}</div>
                <div style="color: gray; font-size: 0.9em;">{time_str}</div>
            </div>
            <div style="margin-top: 6px; font-weight: 600;">
                You are <span style="color: {'blue' if present else 'red'};">{'present' if present else 'absent'}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
