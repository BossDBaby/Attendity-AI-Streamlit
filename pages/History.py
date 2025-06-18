import streamlit as st
from datetime import date, datetime, timedelta
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

# Get today's date
today = date.today()
yesterday = today - timedelta(days=1)

# Add a toggle to view all history or just today's
view_mode = st.radio(
    "View Mode:",
    ["Today's Records", "All History"],
    horizontal=True,
    index=0  # Default to today's records
)

st.markdown("#### History")

session = db_manager.get_session()
try:
    # Query attendance records for this user
    query = session.query(AttendanceRecord).filter(
        AttendanceRecord.student_username == username
    )
    
    # Filter by date if viewing today's records only
    if view_mode == "Today's Records":
        query = query.filter(AttendanceRecord.date == today)
    
    records = query.order_by(AttendanceRecord.date.desc(), AttendanceRecord.time.desc()).all()

    if not records:
        if view_mode == "Today's Records":
            st.info("No attendance records found for today.")
        else:
            st.info("No attendance records found yet.")
        st.stop()

    # Group records by date for better organization
    records_by_date = {}
    for record in records:
        date_str = record.date.strftime("%Y-%m-%d")
        if date_str not in records_by_date:
            records_by_date[date_str] = []
        records_by_date[date_str].append(record)

    # Display records grouped by date (newest first)
    for date_str in sorted(records_by_date.keys(), reverse=True):
        st.markdown(f"**{date_str}**")
        
        for record in records_by_date[date_str]:
            subject = record.subject_name
            time_str = record.time.strftime("%I:%M %p").lstrip('0')  # e.g., "9:30 AM"
            status = record.status
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
                        <div style="color: gray; font-size: 0.9em;">{time_str}</div>
                    </div>
                    <div style="margin-top: 6px; font-weight: 600;">
                        Status: <span style="color: {'blue' if present else 'red'};">{status}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        st.divider()

finally:
    session.close()