import streamlit as st
import face_recognition
import numpy as np
import os
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Attendance - Attendity")

# 🔒 Authentication check
if not st.session_state.get("logged_in"):
    st.switch_page("pages/Login.py")

# Buttons
st.sidebar.markdown("### Account")
st.sidebar.button("🔓 Log Out", on_click=lambda: [st.session_state.clear(), st.rerun()])
st.sidebar.page_link("pages/Home.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/History.py", label="History", icon="📊")
st.sidebar.page_link("pages/Attendance.py", label="Attendance", icon="🧍")

st.title("🧍 Facial Attendance")

def subject_to_filename(subject):
    return subject.strip().replace(' ', '_').lower()

subject = st.session_state.get("selected_subject", None)
if not subject:
    st.warning("No subject selected. Please go back to the Home page.")
    st.stop()

st.subheader(f"Subject: {subject}")

ATTENDANCE_FILE = f"assets/attendance/{subject_to_filename(subject)}.csv"
KNOWN_PATH = "assets/user_photos/"

# 🛠 Admin tools (only if admin)
if st.session_state.get("is_admin"):
    st.sidebar.divider()
    st.sidebar.markdown("### Admin Section")
    st.sidebar.page_link("pages/Admin.py", label="Admin Panel", icon="🛠")

# Load known faces
known_encodings = []
known_names = []

for filename in os.listdir(KNOWN_PATH):
    if filename.lower().endswith((".jpg", ".png")):
        img = face_recognition.load_image_file(os.path.join(KNOWN_PATH, filename))
        encodings = face_recognition.face_encodings(img)
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(filename)[0])

# Load existing attendance data
if os.path.exists(ATTENDANCE_FILE):
    df = pd.read_csv(ATTENDANCE_FILE)
else:
    df = pd.DataFrame(columns=["Name", "Time"])

uploaded_file = st.file_uploader("Upload your face image to mark attendance", type=["jpg", "png"])

if uploaded_file is not None:
    img = face_recognition.load_image_file(uploaded_file)
    encodings = face_recognition.face_encodings(img)

    if len(encodings) == 0:
        st.error("No face detected. Please upload a clear image.")
    else:
        face_encoding = encodings[0]
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            name = known_names[best_match_index]
            now = datetime.now()
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            today_date = now.date()

            already_checked_in = (
                (df['Name'] == name) &
                (pd.to_datetime(df['Time']).dt.date == today_date)
            ).any()

            if already_checked_in:
                st.warning(f"{name} already checked in today!")
            else:
                new_entry = pd.DataFrame([[name, now_str]], columns=["Name", "Time"])
                df = pd.concat([df, new_entry], ignore_index=True)
                df.to_csv(ATTENDANCE_FILE, index=False)
                st.success(f"{name} checked in at {now.strftime('%H:%M:%S')}")
        else:
            st.error("Face does not match any registered user.")
