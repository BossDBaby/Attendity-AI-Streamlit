import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="History - Attendity")

# 🔒 Authentication check
if not st.session_state.get("logged_in"):
    st.switch_page("pages/Login.py")

# Buttons
st.sidebar.markdown("### Account")
st.sidebar.button("🔓 Log Out", on_click=lambda: [st.session_state.clear(), st.rerun()])
st.sidebar.page_link("pages/Home.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/History.py", label="History", icon="📊")

st.title("📊 Attendance History")

ATTENDANCE_FILE = "data/attendance.csv"

# 🛠 Admin tools (only if admin)
if st.session_state.get("is_admin"):
    st.sidebar.divider()
    st.sidebar.markdown("### Admin Section")
    st.sidebar.page_link("pages/Admin.py", label="Admin Panel", icon="🛠")

if not os.path.exists(ATTENDANCE_FILE):
    st.warning("No attendance record found yet.")
else:
    df = pd.read_csv(ATTENDANCE_FILE)

    df['Time'] = pd.to_datetime(df['Time'])
    df = df.sort_values(by='Time', ascending=False)

    st.dataframe(df, use_container_width=True)

    # Filter by name
    names = df['Name'].unique().tolist()
    selected_name = st.selectbox("Filter by Name", options=["All"] + names)

    if selected_name != "All":
        filtered_df = df[df['Name'] == selected_name]
        st.dataframe(filtered_df, use_container_width=True)
