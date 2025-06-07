import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class DatabaseManager:
    def __init__(self):
        self.db_type = os.getenv('DB_TYPE', 'sqlite')
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(bind=self.engine)

    def _create_engine(self):
        if self.db_type == "sqlite":
            return create_engine(
                f"sqlite:///{os.getenv('DB_NAME', 'attendity.db')}",
                connect_args={"check_same_thread": False}
            )
        else:
            raise ValueError(f"Unsupported DB_TYPE: {self.db_type}")

    def get_session(self):
        return self.SessionLocal()

    def init_db(self):
        # Import models so they are registered with Base
        from models.attendance_models import User, Major, Subject, AttendanceRecord
        Base.metadata.create_all(self.engine)

# Global database instance
db_manager = DatabaseManager()
