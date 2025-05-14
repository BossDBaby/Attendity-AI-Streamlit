import streamlit as st
import cv2
import face_recognition
import numpy as np
import os
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Attendance - Attendity")

st.sidebar.page_link("app.py", label="Log Out")
st.sidebar.page_link("pages/Home.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/Attendance.py", label="Attendance", icon="🧍")
st.sidebar.page_link("pages/History.py", label="History", icon="📊")
if st.session_state.get('is_admin'):
    st.sidebar.page_link("pages/4_Admin.py", label="Admin Panel", icon="🛠")

st.title("🧍 Facial Attendance")

# Paths
ATTENDANCE_FILE = "data/attendance.csv"
KNOWN_PATH = "assets/user_photos/"

# Load known faces
known_encodings = []
known_names = []

for filename in os.listdir(KNOWN_PATH):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        img = face_recognition.load_image_file(os.path.join(KNOWN_PATH, filename))
        encodings = face_recognition.face_encodings(img)
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(filename)[0])

# Load existing data
if os.path.exists(ATTENDANCE_FILE):
    df = pd.read_csv(ATTENDANCE_FILE)
else:
    df = pd.DataFrame(columns=["Name", "Time"])

# Webcam
start = st.button("Start Attendance")
if start:
    st.info("Starting camera... press Q to stop.")
    cam = cv2.VideoCapture(0)

    while True:
        ret, frame = cam.read()
        if not ret:
            st.error("Failed to access webcam.")
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, faces)

        for face_encoding, face_loc in zip(encodings, faces):
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            name = "Unknown"

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

        # Show preview
        cv2.imshow("Attendance Camera - Press Q to stop", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()
