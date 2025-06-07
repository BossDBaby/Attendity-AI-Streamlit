import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
from config.database import db_manager
from models.attendance_models import AttendanceRecord

st.set_page_config(page_title="Admin Attendance History - Attendity")

# Authentication check
if not st.session_state.get("logged_in"):
    st.switch_page("pages/Login.py")

# 🔒 Protect the page
if not st.session_state.get("logged_in") or not st.session_state.get("is_admin"):
    st.switch_page("pages/Home.py")

st.title("🛠 Admin: Full Attendance History")

# Sidebar Navigation
st.sidebar.markdown("### Account")
st.sidebar.button("🔓 Log Out", on_click=lambda: [st.session_state.clear(), st.rerun()])
st.sidebar.page_link(label="Home 🏠", page="pages/Home.py")
st.sidebar.page_link(label="History 📊", page= "pages/History.py")
st.sidebar.page_link(label="Attendance 🧍", page= "pages/Attendance.py")
st.sidebar.divider()
st.sidebar.markdown("### Admin Section")
st.sidebar.page_link(label="Admin Panel 🛠", page="pages/Admin.py")
st.sidebar.page_link(label="Admin Attendance History 🛠", page="pages/Admin_Attendance_HIstory.py")

# Get filter inputs
with st.sidebar.expander("Filters"):
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", date.today().replace(day=1))
    with col2:
        end_date = st.date_input("End date", date.today())

    username_filter = st.text_input("Filter by username (partial match)")
    subject_filter = st.text_input("Filter by subject (partial match)")

# Pagination controls
PER_PAGE = 10
page = st.number_input("Page number", min_value=1, step=1, value=1)

# Fetch data
session = db_manager.get_session()
try:
    query = session.query(AttendanceRecord)

    # Filter by date range
    if start_date:
        query = query.filter(AttendanceRecord.date >= start_date)
    if end_date:
        query = query.filter(AttendanceRecord.date <= end_date)

    # Convert to list for further filtering
    records = query.all()

    # Filter by username (partial, case-insensitive)
    if username_filter:
        records = [r for r in records if username_filter.lower() in (r.student_username or "").lower()]

    # Filter by subject (partial, case-insensitive)
    if subject_filter:
        records = [r for r in records if subject_filter.lower() in (r.subject_name or "").lower()]

    total_records = len(records)
    total_pages = (total_records + PER_PAGE - 1) // PER_PAGE

    # Paginate
    start_idx = (page - 1) * PER_PAGE
    end_idx = start_idx + PER_PAGE
    records_page = records[start_idx:end_idx]

    if not records_page:
        st.info("No attendance records found for the current filters and page.")
    else:
        data = []
        for r in records_page:
            data.append({
                "ID": r.id,
                "Username": r.student_username,
                "Subject": r.subject_name,
                "Date": r.date.strftime("%Y-%m-%d"),
                "Time": r.time.strftime("%H:%M:%S"),
                "Status": r.status
            })
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        st.markdown(f"Showing page {page} of {total_pages} ({total_records} records total)")

    # Export all filtered records to CSV
    if records:
        all_data = [{
            "ID": r.id,
            "Username": r.student_username,
            "Subject": r.subject_name,
            "Date": r.date.strftime("%Y-%m-%d"),
            "Time": r.time.strftime("%H:%M:%S"),
            "Status": r.status
        } for r in records]

        df_all = pd.DataFrame(all_data)
        os.makedirs("assets/attendance", exist_ok=True)
        csv_filename = f"assets/attendance/attendance_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        if st.button("Export Filtered Records to CSV"):
            df_all.to_csv(csv_filename, index=False)
            st.success(f"Exported filtered records to `{csv_filename}`")

            with open(csv_filename, "rb") as f:
                st.download_button("Download CSV file", f, file_name=os.path.basename(csv_filename))

finally:
    session.close()
