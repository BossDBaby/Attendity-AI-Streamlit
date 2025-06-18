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

1. Clone the repository
2. Create a virtual environment and activate it
3. Install the required dependencies using `pip install -r requirements.txt`
4. Run the app using `streamlit run app.py`

## 📝 Usage

1. Go to the `Login` page and log in using your credentials
2. Go to the `Home` page and select the subject you want to check in for
3. Take a picture of your face using the webcam or upload a photo of your face
4. The app will check if your face matches with the known student photos and mark your attendance if it does

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
