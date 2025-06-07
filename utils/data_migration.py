import json
from config.database import db_manager
from models.attendance_models import User, Major, Subject
import bcrypt

def migrate_json_to_database():
    """Migrate existing users.json to database"""
    session = db_manager.get_session()

    try:
        # Read existing users.json
        with open('data/users.json', 'r') as f:
            users_data = json.load(f)

        # Create sample major first
        major = Major(name="Computer Science", code="CS")
        session.add(major)
        session.flush()  # get major.id

        # Migrate users with major_id assignment
        for username, user_data in users_data.items():
            user = User(
                username=username,
                name=user_data['name'],
                email=user_data.get('email', ''),
                password_hash=user_data['password'],  # Already hashed in your JSON, no need to rehash
                role=user_data.get('role', 'student'),
                major_id=major.id
            )
            session.add(user)

        # Add subjects linked to major
        subjects_data = [
            ("UI-UX", "09:30 AM"),
            ("Project", "10:40 AM"),
            ("AI", "11:45 AM"),
            ("Cyber Security", "12:10 PM"),
            ("Ethical Hacking", "12:45 PM"),
            ("Software Engineering", "13:30 PM")
        ]

        for subject_name, time in subjects_data:
            subject = Subject(
                name=subject_name,
                schedule_time=time,
                major_id=major.id
            )
            session.add(subject)

        session.commit()
        print("Migration completed successfully!")

    except Exception as e:
        session.rollback()
        print(f"Migration failed: {e}")
    finally:
        session.close()
