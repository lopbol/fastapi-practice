from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from datetime import datetime
from database import Base
from sqlalchemy.orm import relationship

class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)  # ← уникальный
    name = Column(String(50), nullable=False)
    age = Column(Integer)
    hashed_password = Column(String(255), nullable=False)     # ← вместо password
    created_at = Column(DateTime, default=datetime.now)

    sets = relationship("WorkoutSetDB", back_populates="user", cascade="all, delete-orphan")

class ExerciseDB(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    muscle_group = Column(String(200))
    
    approach = relationship("WorkoutSetDB", back_populates="exercise", cascade='all, delete-orphan')

class WorkoutSetDB(Base):
    __tablename__ = "workoutSets"

    id = Column(Integer, primary_key=True, index=True)
    weight = Column(Float, nullable=False)
    reps = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))

    user = relationship("UserDB", back_populates="sets")
    exercise = relationship("ExerciseDB", back_populates="approach")
