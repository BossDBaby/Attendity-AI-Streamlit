import streamlit as st
import face_recognition
import numpy as np
import os
import pandas as pd
from datetime import datetime
from face_recognition_model import load_user_encoding
from PIL import Image

st.set_page_config(page_title="Attendance - Attendity")

# Constants
FACE_MATCH_THRESHOLD = 0.6  # Smaller is stricter

# 🔒 Authentication check
if not st.session_state.get("logged_in"):
    st.switch_page("pages/Login.py")

# Sidebar Navigation
st.sidebar.markdown("### Account")
st.sidebar.button("🔓 Log Out", on_click=lambda: [st.session_state.clear(), st.rerun()])
st.sidebar.page_link("pages/Home.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/History.py", label="History", icon="📊")
st.sidebar.page_link("pages/Attendance.py", label="Attendance", icon="🧍")

# 🛠 Admin tools
if st.session_state.get("is_admin"):
    st.sidebar.divider()
    st.sidebar.markdown("### Admin Section")
    st.sidebar.page_link("pages/Admin.py", label="Admin Panel", icon="🛠")

st.title("🧍 Facial Attendance")

# 📚 Get selected subject
def subject_to_filename(subject):
    return subject.strip().replace(' ', '_').lower()

subject = st.session_state.get("selected_subject")
if not subject:
    st.warning("No subject selected. Please go back to the Home page.")
    st.stop()

st.subheader(f"Subject: {subject}")

# Attendance CSV path
ATTENDANCE_FILE = f"assets/attendance/{subject_to_filename(subject)}.csv"
os.makedirs(os.path.dirname(ATTENDANCE_FILE), exist_ok=True)

# Load or initialize CSV
if os.path.exists(ATTENDANCE_FILE):
    df = pd.read_csv(ATTENDANCE_FILE)
else:
    df = pd.DataFrame(columns=["Name", "Time"])

# Load face encoding
username = st.session_state.get("username")
user_encoding = load_user_encoding(username)

if user_encoding is None:
    st.error(f"No valid face encodings found for {username}. Please contact admin.")
    st.stop()

st.markdown("### Mark your attendance")
st.info("You can either upload your face image or take a snapshot using your webcam.")

# --- Webcam snapshot ---
img_file_buffer = st.camera_input("Take a picture")

def process_face_image(image):
    if isinstance(image, Image.Image):
        img = np.array(image)
    else:
        img = image

    face_encodings = face_recognition.face_encodings(img)

    if not face_encodings:
        st.error("No face detected. Please provide a clearer image.")
        return

    uploaded_encoding = face_encodings[0]
    distance = face_recognition.face_distance([user_encoding], uploaded_encoding)[0]
    confidence = 1 - distance

    if distance <= FACE_MATCH_THRESHOLD:
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        today = now.date()

        already_checked_in = (
            (df['Name'] == username) &
            (pd.to_datetime(df['Time']).dt.date == today)
        ).any()

        if already_checked_in:
            st.warning(f"{username} already checked in today!")
        else:
            df.loc[len(df.index)] = [username, now_str]
            df.to_csv(ATTENDANCE_FILE, index=False)
            st.success(f"{username} checked in at {now.strftime('%H:%M:%S')}")
        st.info(f"Recognition confidence: {confidence:.2f}")
    else:
        st.error("Face does not match your registered photo.")
        st.info(f"Recognition confidence: {confidence:.2f}")

# If image from webcam
if img_file_buffer is not None:
    image = Image.open(img_file_buffer)
    st.image(image, caption="Captured Image", use_column_width=True)
    process_face_image(np.array(image)[:, :, ::-1])  # Convert RGB to BGR

# --- File upload option ---
uploaded_file = st.file_uploader("Or upload your face image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    uploaded_img = face_recognition.load_image_file(uploaded_file)
    st.image(uploaded_img, caption="Uploaded Image", use_column_width=True)
    process_face_image(uploaded_img)
