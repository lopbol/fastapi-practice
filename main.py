from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
import uvicorn

from database import Base, engine, get_db
from models import UserDB
from schemas import UserRegister, UserLogin, UserResponse
from security import hash_password, verify_password

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # 1. Проверить, что email свободен
    existing = db.query(UserDB).filter(UserDB.email == user_data.email).first()
    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail="Email уже зарегистрирован"
        )
    
    # 2. Создать пользователя с хешированным паролем
    db_user = UserDB(
        email=user_data.email,
        name=user_data.name,
        age=user_data.age,
        hashed_password=hash_password(user_data.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # 1. Найти пользователя
    user = db.query(UserDB).filter(UserDB.email == credentials.email).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль"
        )
    
    # 2. Проверить пароль
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль"
        )
    
    # 3. Успех
    return {
        "message": "Успешный вход",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)