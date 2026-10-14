from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    age = Column(Integer)
    email = Column(String(150), default="Не указан")
    created_at = Column(DateTime, default=datetime.now)