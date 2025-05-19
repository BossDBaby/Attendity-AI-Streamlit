import face_recognition
import os
import numpy as np

KNOWN_PATH = "assets/user_photos/"

def load_user_encoding(username):
    # Loads and averages all encodings for a specific user from their folder.
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

    # Average encoding across multiple images
    return np.mean(encodings, axis=0)
