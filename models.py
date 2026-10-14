from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)  # ← уникальный
    name = Column(String(50), nullable=False)
    age = Column(Integer)
    hashed_password = Column(String(255), nullable=False)     # ← вместо password
    created_at = Column(DateTime, default=datetime.now)