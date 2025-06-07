import streamlit as st
from datetime import date
from config.database import db_manager
from models.attendance_models import AttendanceRecord, Subject

st.set_page_config(page_title="History - Attendity")

# 🔒 Authentication check
if not st.session_state.get("logged_in"):
    st.switch_page("pages/Login.py")

# Sidebar Navigation
st.sidebar.markdown("### Account")
st.sidebar.button("🔓 Log Out", on_click=lambda: [st.session_state.clear(), st.rerun()])
st.sidebar.page_link("pages/Home.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/History.py", label="History", icon="📊")

# Admin Section in Sidebar
if st.session_state.get("is_admin"):
    st.sidebar.divider()
    st.sidebar.markdown("### Admin Section")
    st.sidebar.page_link("pages/Admin.py", label="Admin Panel", icon="🛠")

st.title("📊 Your Attendance History")

username = st.session_state.get("username")
if not username:
    st.error("User not logged in.")
    st.stop()

st.markdown(f"### Student: **{username}**")
st.markdown("#### History")

session = db_manager.get_session()
try:
    # Query all attendance records for this user
    records = session.query(AttendanceRecord).filter(
        AttendanceRecord.student_username == username
    ).all()

    if not records:
        st.info("No attendance records found yet.")
        st.stop()

    # Map subject_name -> latest attendance record info
    attendance_summary = {}
    for record in records:
        subject = record.subject_name  # Correct attribute name
        # Update only if newer attendance time for that subject
        if subject not in attendance_summary or record.date > attendance_summary[subject]["date"] or \
           (record.date == attendance_summary[subject]["date"] and record.time > attendance_summary[subject]["time"]):
            attendance_summary[subject] = {
                "time": record.time,
                "date": record.date,
                "status": record.status
            }

    # Display summary
    for subject in sorted(attendance_summary.keys()):
        record = attendance_summary[subject]
        time_str = record["time"].strftime("%I:%M %p").lstrip('0')  # e.g., "9:30 AM"
        date_str = record["date"].strftime("%Y-%m-%d")  # ISO style date
        status = record["status"]
        present = status.lower() == "present"

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
                    <div style="color: gray; font-size: 0.9em;">{date_str} | {time_str}</div>
                </div>
                <div style="margin-top: 6px; font-weight: 600;">
                    You are <span style="color: {'blue' if present else 'red'};">{status}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
finally:
    session.close()
