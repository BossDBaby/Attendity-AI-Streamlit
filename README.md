# Attendity 📷🧑‍🏫

Attendity is a facial-recognition based student attendance system built using Streamlit and Python 3.10.17.

## ✨ Features

- Secure login system
- Class schedule view
- Face recognition-based attendance check-in
- Attendance history tracking
- Clean responsive UI

## 🧠 Face Recognition

Uses `face_recognition` (dlib) to match real-time webcam input with known student photos.
Photos of the student is save on assets folder using this format: `assets/user_photos/<student_id>.jpg`

## 🛠 Setup Instructions

pip install -r requirements.txt
streamlit run app.py
