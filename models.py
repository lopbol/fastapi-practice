from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
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

    posts = relationship("PostDB", back_populates="author", cascade="all, delete-orphan")

class PostDB(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(String(2000))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    author = relationship("UserDB", back_populates="posts")
