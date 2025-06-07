from mtcnn import MTCNN
import face_recognition
import os
import numpy as np

# Paths
KNOWN_PATH = "assets/user_photos/"
ENCODINGS_PATH = "assets/encodings/"

os.makedirs(ENCODINGS_PATH, exist_ok=True)

# Initialize MTCNN detector once
detector = MTCNN()

def extract_face_encodings(image, padding=20):
    """
    Detect faces using MTCNN and compute face embeddings with face_recognition.
    Adds padding to bounding box to improve face crop quality.
    Returns a list of encodings found in the image.
    """
    height, width = image.shape[:2]

    encodings = []
    detections = detector.detect_faces(image)
    for det in detections:
        x, y, w, h = det['box']

        # Add padding and clamp to image boundaries
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(width, x + w + padding)
        y2 = min(height, y + h + padding)

        # face_recognition expects (top, right, bottom, left)
        top = y1
        right = x2
        bottom = y2
        left = x1

        # Compute face encoding for detected face region
        face_encs = face_recognition.face_encodings(
            image,
            known_face_locations=[(top, right, bottom, left)],
            model="cnn"  # use "cnn" if you have GPU, else "small"
        )
        if face_encs:
            encodings.append(face_encs[0])
    return encodings


def load_user_encoding(username):
    """
    Load or compute and cache the average face encoding for a user.
    """
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
            try:
                image = face_recognition.load_image_file(path)
                face_encs = extract_face_encodings(image)
                encodings.extend(face_encs)
            except Exception as e:
                print(f"[Warning] Failed to process {path}: {e}")

    if not encodings:
        return None

    avg_encoding = np.mean(encodings, axis=0)
    np.save(cached_file, avg_encoding)
    return avg_encoding


def regenerate_all_encodings():
    """
    Regenerate cached encodings for all users.
    """
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
                    try:
                        image = face_recognition.load_image_file(path)
                        face_encs = extract_face_encodings(image)
                        encodings.extend(face_encs)
                    except Exception as e:
                        print(f"[Warning] Failed to process {path}: {e}")

            if encodings:
                avg_encoding = np.mean(encodings, axis=0)
                np.save(os.path.join(ENCODINGS_PATH, f"{username}.npy"), avg_encoding)
                count += 1

    return count


# --- Example usage for matching with adjustable threshold ---
def is_match(known_encoding, unknown_encoding, threshold=0.6):
    """
    Compare known and unknown face encodings with a threshold.
    Returns True if distance is below threshold.
    """
    distance = np.linalg.norm(known_encoding - unknown_encoding)
    return distance < threshold
