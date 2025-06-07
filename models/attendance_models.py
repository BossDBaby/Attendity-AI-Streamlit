from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Date, Time
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='student')  # admin, teacher, student
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=True)  # New field for Major
    created_at = Column(DateTime, default=datetime.utcnow)
    
    major = relationship("Major", back_populates="users", uselist=False)  # relationship to Major

class Major(Base):
    __tablename__ = "majors"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True)
    
    subjects = relationship("Subject", back_populates="major")
    users = relationship("User", back_populates="major")  # reverse relation to User

class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    schedule_time = Column(String(20))  # "09:30 AM"
    major_id = Column(Integer, ForeignKey("majors.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    
    major = relationship("Major", back_populates="subjects")
    teacher = relationship("User")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True)
    
    # Foreign Keys
    student_id = Column(Integer, ForeignKey("users.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    
    # Redundant readable fields
    student_username = Column(String(50))   # denormalized
    subject_name = Column(String(100))      # denormalized
    
    date = Column(Date, default=datetime.utcnow().date)
    time = Column(Time, default=datetime.utcnow().time)
    status = Column(String(20), default='present')
    
    student = relationship("User")
    subject = relationship("Subject")