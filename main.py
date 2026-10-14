from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import uvicorn

from database import Base, engine, get_db
from models import UserDB
from schemas import UserCreate, UserResponse

# Создать таблицы
Base.metadata.create_all(bind=engine)

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
    db_user = UserDB(name=user.name, age=user.age, email=user.email)
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