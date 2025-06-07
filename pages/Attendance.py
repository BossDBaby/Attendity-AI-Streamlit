import streamlit as st
import face_recognition
import numpy as np
import os
from datetime import datetime, date
from face_recognition_model import load_user_encoding
from PIL import Image
import cv2
from config.database import db_manager
from models.attendance_models import AttendanceRecord, Subject, User
from mtcnn import MTCNN

st.set_page_config(page_title="Attendance - Attendity")

# Constants
FACE_MATCH_THRESHOLD = 0.55  # Increase this value to be more strict
PADDING = 20  # pixels for face crop padding

# Initialize MTCNN detector once
detector = MTCNN()

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

# Database helper functions
def get_subject_id(subject_name):
    """Get subject ID from database"""
    session = db_manager.get_session()
    try:
        subject = session.query(Subject).filter(Subject.name == subject_name).first()
        return subject.id if subject else None
    finally:
        session.close()

def get_user_id(username):
    """Get user ID from database"""
    session = db_manager.get_session()
    try:
        user = session.query(User).filter(User.username == username).first()
        return user.id if user else None
    finally:
        session.close()

def check_attendance_exists(user_id, subject_id, attendance_date):
    """Check if attendance record exists for today"""
    session = db_manager.get_session()
    try:
        existing = session.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == user_id,
            AttendanceRecord.subject_id == subject_id,
            AttendanceRecord.date == attendance_date
        ).first()
        return existing is not None
    finally:
        session.close()

def save_attendance_record(user_id, subject_id):
    session = db_manager.get_session()
    try:
        now = datetime.now()

        user = session.query(User).filter_by(id=user_id).first()
        subject = session.query(Subject).filter_by(id=subject_id).first()

        if not user or not subject:
            st.error("User or subject not found.")
            return False

        record = AttendanceRecord(
            student_id=user.id,
            subject_id=subject.id,
            student_username=user.username if user else None,  # denormalized
            subject_name=subject.name if subject else None,    # denormalized
            date=now.date(),
            time=now.time(),
            status='present'
        )
        session.add(record)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        st.error(f"Database error: {str(e)}")
        return False
    finally:
        session.close()

# 📚 Get selected subject
subject = st.session_state.get("selected_subject")
if not subject:
    st.warning("No subject selected. Please go back to the Home page.")
    st.stop()

st.subheader(f"Subject: {subject}")

# Get database IDs
username = st.session_state.get("username")
user_id = get_user_id(username)
subject_id = get_subject_id(subject)

if not user_id:
    st.error(f"User {username} not found in database. Please contact admin.")
    st.stop()

if not subject_id:
    st.error(f"Subject {subject} not found in database. Please contact admin.")
    st.stop()

# Load face encoding
user_encoding = load_user_encoding(username)

if user_encoding is None:
    st.error(f"No valid face encodings found for {username}. Please contact admin.")
    st.stop()

st.markdown("### Mark your attendance")
st.info("You can either upload your face image or take a snapshot using your webcam.")

# Utility: Resize image
def resize_image(image_np, max_width=640):
    height, width = image_np.shape[:2]
    if width > max_width:
        ratio = max_width / width
        new_size = (int(width * ratio), int(height * ratio))
        return cv2.resize(image_np, new_size)
    return image_np

def extract_face_encodings_with_padding(image_np, padding=PADDING):
    """
    Detect faces using MTCNN and compute face encodings with padding.
    Returns a list of encodings found.
    """
    height, width = image_np.shape[:2]
    encodings = []
    detections = detector.detect_faces(image_np)
    for det in detections:
        x, y, w, h = det['box']

        # Add padding and clamp coordinates
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(width, x + w + padding)
        y2 = min(height, y + h + padding)

        top, right, bottom, left = y1, x2, y2, x1

        face_encs = face_recognition.face_encodings(
            image_np,
            known_face_locations=[(top, right, bottom, left)],
            model="cnn"
        )
        if face_encs:
            encodings.append(face_encs[0])
    return encodings

def is_match(known_encoding, unknown_encoding, threshold=FACE_MATCH_THRESHOLD):
    distance = np.linalg.norm(known_encoding - unknown_encoding)
    return distance < threshold, 1 - distance  # (bool match, confidence)

def process_face_image(image_np):
    try:
        image_np = resize_image(image_np)

        with st.spinner("Processing image..."):
            face_encodings = extract_face_encodings_with_padding(image_np)

            if not face_encodings:
                st.error("No face detected. Please provide a clearer image.")
                return
            elif len(face_encodings) > 1:
                st.error("Multiple faces detected. Please ensure only one face is visible.")
                return

            uploaded_encoding = face_encodings[0]
            match, confidence = is_match(user_encoding, uploaded_encoding)

            if match:
                now = datetime.now()
                today = now.date()

                already_checked_in = check_attendance_exists(user_id, subject_id, today)

                if already_checked_in:
                    st.warning(f"{username} already checked in today for {subject}!")
                else:
                    if save_attendance_record(user_id, subject_id):
                        st.success(f"✅ {username} checked in at {now.strftime('%H:%M:%S')}")
                        st.balloons()
                    else:
                        st.error("Failed to save attendance record. Please try again.")

                st.info(f"Recognition confidence: {confidence:.2f}")
            else:
                st.error("Face does not match your registered photo.")
                st.info(f"Recognition confidence: {confidence:.2f}")
    except Exception as e:
        st.error(f"Error during face processing: {str(e)}")

# --- Webcam snapshot ---
img_file_buffer = st.camera_input("Take a picture")

if img_file_buffer is not None:
    try:
        image = Image.open(img_file_buffer)
        st.image(image, caption="Captured Image", use_column_width=True)
        image_np = np.array(image)[:, :, ::-1]  # Convert RGB to BGR for face_recognition
        process_face_image(image_np)
    except Exception as e:
        st.error(f"Error loading webcam image: {str(e)}")

# --- File upload option ---
uploaded_file = st.file_uploader("Or upload your face image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        uploaded_img = face_recognition.load_image_file(uploaded_file)
        st.image(uploaded_img, caption="Uploaded Image", use_column_width=True)
        process_face_image(uploaded_img)
    except Exception as e:
        st.error(f"Error loading uploaded image: {str(e)}")

# ✅ Admin-only: Display today's attendance summary
if st.session_state.get("is_admin"):
    with st.expander("📊 Today's Attendance Summary"):
        session = db_manager.get_session()
        try:
            today_records = session.query(AttendanceRecord).join(User).filter(
                AttendanceRecord.subject_id == subject_id,
                AttendanceRecord.date == date.today()
            ).all()

            if today_records:
                st.write(f"**{len(today_records)} students** have checked in for {subject} today:")
                for record in today_records:
                    st.write(f"• {record.student_username} at {record.time.strftime('%H:%M:%S')}")
            else:
                st.write("No attendance records for today yet.")
        finally:
            session.close()
