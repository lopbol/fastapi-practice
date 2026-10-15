from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uvicorn

from database import Base, engine, get_db
from models import UserDB
from schemas import UserRegister, UserLogin, UserResponse, Token, UpdateUser
from security import hash_password, verify_password, create_access_token, decode_token

Base.metadata.create_all(bind=engine)

app = FastAPI()

security = HTTPBearer(scheme_name="JWT")

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> UserDB:
    token = credentials.credentials      # ← возвращаем .credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или истёкший токен",
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Токен без sub")
    user = db.query(UserDB).filter(UserDB.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user

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
    access_token = create_access_token(user_id = user.id)
    # 3. Успех
    return {"access_token": access_token, "token_type": "bearer"}


@app.patch("/users/me", response_model=UserResponse)
def update(user_data: UpdateUser, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_data.name is not None:
        current_user.name = user_data.name
    if user_data.age is not None:
        current_user.age = user_data.age
    db.commit()
    db.refresh(current_user)
    return current_user

@app.delete("/users/me", status_code=204)
def delite_users(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(current_user)
    db.commit()
    return None



@app.get("/users/me", response_model=UserResponse)
def get_me(current_user: UserDB = Depends(get_current_user)):
    return current_user

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)