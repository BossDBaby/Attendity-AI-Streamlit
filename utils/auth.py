import bcrypt
from config.database import db_manager
from models.attendance_models import User, Subject  # ✅ Fixed import

def authenticate_user(username, password):
    """Database-based authentication"""
    session = db_manager.get_session()
    try:
        user = session.query(User).filter(User.username == username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return {
                "user_id": user.id,
                "username": user.username,
                "name": user.name,
                "role": user.role,
                "email": user.email
            }
        return None
    finally:
        session.close()

def get_user_subjects(user_id, role):
    session = db_manager.get_session()
    try:
        if role == "admin":
            subjects = session.query(Subject).all()
        elif role == "teacher":
            subjects = session.query(Subject).filter(Subject.teacher_id == user_id).all()
        else:  # student
            student = session.query(User).filter(User.id == user_id).first()
            if student and student.major_id:
                subjects = session.query(Subject).filter(Subject.major_id == student.major_id).all()
            else:
                subjects = []
        return [(s.name, s.schedule_time) for s in subjects]
    finally:
        session.close()

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt and return the hashed string."""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')
