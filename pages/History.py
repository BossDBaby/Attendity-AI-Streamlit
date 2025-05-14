import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="History - Attendity")

st.sidebar.page_link("app.py", label="Log Out")
st.sidebar.page_link("pages/Home.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/Attendance.py", label="Attendance", icon="🧍")
st.sidebar.page_link("pages/History.py", label="History", icon="📊")

st.title("📊 Attendance History")

ATTENDANCE_FILE = "data/attendance.csv"

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
