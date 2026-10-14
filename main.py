from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import uvicorn
from datetime import datetime

# ========DATABASE============
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine, autoflush=True, autocommit=False)
Base = declarative_base()

#=========Models========
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    age = Column(Integer())
    email = Column(String(150), default="Не указан")
    created_at = Column(DateTime, default=datetime.now)

Base.metadata.create_all(bind=engine)

#=======Pydanic======
class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=0, le=150)
    email: str = "Не указан"
    created_at: datetime

class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

#=====depends=====
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#==========app=======
app = FastAPI()


# READ ALL
@app.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(UserDB).all()

# READ ONE
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

# CREATE
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = UserDB(name = user.name, age = user.age, email = user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# UPDATE
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    db_user.name = user.name
    db_user.age = user.age
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    return db_user

# DELETE
@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    db.delete(db_user)
    db.commit()
    return None

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)