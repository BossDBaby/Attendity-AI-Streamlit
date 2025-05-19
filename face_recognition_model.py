import face_recognition
import os
import numpy as np

KNOWN_PATH = "assets/user_photos/"
ENCODINGS_PATH = "assets/encodings/"

os.makedirs(ENCODINGS_PATH, exist_ok=True)

def load_user_encoding(username):
    cached_file = os.path.join(ENCODINGS_PATH, f"{username}.npy")
    if os.path.exists(cached_file):
        return np.load(cached_file)

    user_folder = os.path.join(KNOWN_PATH, username)
    if not os.path.isdir(user_folder):
        return None

    encodings = []
    
    for file in os.listdir(user_folder):
        if file.lower().endswith((".jpg", ".png")):
            path = os.path.join(user_folder, file)
            image = face_recognition.load_image_file(path)
            face_encs = face_recognition.face_encodings(image)
            if face_encs:
                encodings.append(face_encs[0])

    if not encodings:
        return None

    avg_encoding = np.mean(encodings, axis=0)
    np.save(cached_file, avg_encoding)

    return avg_encoding

def regenerate_all_encodings():
    if not os.path.exists(KNOWN_PATH):
        return 0

    count = 0
    for username in os.listdir(KNOWN_PATH):
        user_folder = os.path.join(KNOWN_PATH, username)
        if os.path.isdir(user_folder):
            encodings = []
            for file in os.listdir(user_folder):
                if file.lower().endswith((".jpg", ".png")):
                    path = os.path.join(user_folder, file)
                    image = face_recognition.load_image_file(path)
                    face_encs = face_recognition.face_encodings(image)
                    if face_encs:
                        encodings.append(face_encs[0])

            if encodings:
                avg_encoding = np.mean(encodings, axis=0)
                np.save(os.path.join(ENCODINGS_PATH, f"{username}.npy"), avg_encoding)
                count += 1

    return count
