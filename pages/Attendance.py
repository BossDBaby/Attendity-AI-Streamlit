import streamlit as st
import face_recognition
import numpy as np
import os
import pandas as pd
from datetime import datetime
from face_recognition_model import load_user_encoding

st.set_page_config(page_title="Attendance - Attendity")

# Constants
FACE_MATCH_THRESHOLD = 0.6  # Smaller is stricter (e.g., 0.6 = good match)

# 🔒 Authentication check
if not st.session_state.get("logged_in"):
    st.switch_page("pages/Login.py")

# Sidebar Navigation
st.sidebar.markdown("### Account")
st.sidebar.button("🔓 Log Out", on_click=lambda: [st.session_state.clear(), st.rerun()])
st.sidebar.page_link("pages/Home.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/History.py", label="History", icon="📊")
st.sidebar.page_link("pages/Attendance.py", label="Attendance", icon="🧍")

st.title("🧍 Facial Attendance")

def subject_to_filename(subject):
    return subject.strip().replace(' ', '_').lower()

# 📚 Get selected subject
subject = st.session_state.get("selected_subject", None)
if not subject:
    st.warning("No subject selected. Please go back to the Home page.")
    st.stop()

st.subheader(f"Subject: {subject}")

ATTENDANCE_FILE = f"assets/attendance/{subject_to_filename(subject)}.csv"
os.makedirs(os.path.dirname(ATTENDANCE_FILE), exist_ok=True)

# 🛠 Admin tools
if st.session_state.get("is_admin"):
    st.sidebar.divider()
    st.sidebar.markdown("### Admin Section")
    st.sidebar.page_link("pages/Admin.py", label="Admin Panel", icon="🛠")

# Load user's registered face
username = st.session_state.get("username")
user_encoding = load_user_encoding(username)

if user_encoding is None:
    st.error(f"No valid face encodings found for {username}. Please contact admin.")
    st.stop()

# Load attendance
if os.path.exists(ATTENDANCE_FILE):
    df = pd.read_csv(ATTENDANCE_FILE)
else:
    df = pd.DataFrame(columns=["Name", "Time"])

# Face upload
uploaded_file = st.file_uploader("Upload your face image to mark attendance", type=["jpg", "png"])

if uploaded_file is not None:
    img = face_recognition.load_image_file(uploaded_file)
    encodings = face_recognition.face_encodings(img)

    if not encodings:
        st.error("No face detected. Please upload a clear image.")
    else:
        uploaded_encoding = encodings[0]
        distance = face_recognition.face_distance([user_encoding], uploaded_encoding)[0]
        confidence = 1 - distance

        if distance <= FACE_MATCH_THRESHOLD:
            name = username
            now = datetime.now()
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            today = now.date()

            already_checked_in = (
                (df['Name'] == name) &
                (pd.to_datetime(df['Time']).dt.date == today)
            ).any()

            if already_checked_in:
                st.warning(f"{name} already checked in today!")
            else:
                new_entry = pd.DataFrame([[name, now_str]], columns=["Name", "Time"])
                df = pd.concat([df, new_entry], ignore_index=True)
                df.to_csv(ATTENDANCE_FILE, index=False)
                st.success(f"{name} checked in at {now.strftime('%H:%M:%S')}")
            st.info(f"Recognition confidence: {confidence:.2f}")
        else:
            st.error("Face does not match your registered photo.")
            st.info(f"Recognition confidence: {confidence:.2f}")
