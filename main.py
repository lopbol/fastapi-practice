from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uvicorn
from sqlalchemy import func 

from database import Base, engine, get_db
from models import UserDB, ExerciseDB, WorkoutSetDB
from schemas import UserRegister, UserLogin, UserResponse, Token, UpdateUser, ExerciseCreate, ExerciseResponse, WorkoutSetCreate, WorkoutSetResponse
from security import hash_password, verify_password, create_access_token, decode_token

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

@app.get("/users/me/workouts", response_model=list[WorkoutSetResponse])
def get_my_workouts(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    workout = db.query(WorkoutSetDB).filter(WorkoutSetDB.user_id == current_user.id).order_by(WorkoutSetDB.date.desc()).all()
    return workout

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
def delite_me(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(current_user)
    db.commit()
    return None

@app.get("/users/me", response_model=UserResponse)
def get_me(current_user: UserDB = Depends(get_current_user)):
    return current_user

#Ручки дял упражнений
@app.post("/exercise", response_model=ExerciseResponse, status_code=201)
def create_exercise(exercise_data: ExerciseCreate, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    new_exercise = ExerciseDB(
            name=exercise_data.name,
            muscle_group=exercise_data.muscle_group
            )
    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)
    return new_exercise

@app.get("/exercise", )
def get_all_exercise(db: Session = Depends(get_db)):
    return db.query(ExerciseDB).all()

#Ручки для тренировок
@app.post("/workouts", response_model=WorkoutSetResponse, status_code=201)
def create_workouts(workouts_data: WorkoutSetCreate, current_user: UserDB = Depends(get_current_user),  db: Session = Depends(get_db)):
    new_workouts = WorkoutSetDB(
                weight=workouts_data.weight,
                reps=workouts_data.reps,
                exercise_id = workouts_data.exercise_id,
                user_id = current_user.id
                )
    p = db.query(ExerciseDB).filter(ExerciseDB.id == workouts_data.exercise_id).first()
    if p is None:
        raise HTTPException(status_code=404, detail="Пост не найден")
    db.add(new_workouts)
    db.commit()
    db.refresh(new_workouts)
    return new_workouts
    


@app.get("/workouts/stats/{exercise_id}")
def get_my_stats(exercise_id: int, current_user: UserDB = Depends(get_current_user),  db: Session = Depends(get_db)):
    s = db.query(ExerciseDB).filter(ExerciseDB.id == exercise_id).first()
    if s is None:
        raise HTTPException(status_code=404, detail='Упражнение не найдено')
    stats = db.query(
        func.max(WorkoutSetDB.weight),
        func.count(WorkoutSetDB.id),
        func.sum(WorkoutSetDB.reps)
    ).filter(WorkoutSetDB.user_id == current_user.id, WorkoutSetDB.exercise_id == exercise_id).first()
    return {
        "max_weight": stats[0],
        "total_sets": stats[1],
        "total_reps": stats[2]
    }

@app.delete("/workouts/{set_id}", status_code=204)
def delete_my_workout(set_id: int, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    sets = db.query(WorkoutSetDB).filter(WorkoutSetDB.id==set_id).first()
    if sets is None:
        raise HTTPException(status_code=404, detail="Подход не найден")
    if sets.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нельзя удалить чужой подход")
    db.delete(sets)
    db.commit()
    return None

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

'''ОСТАЛОСЬ ДОДЕЛАТЬ ЭТОТ ФАЙЛ ИСПРАВИТЬ РУЧКИ!!!!!!!!!!!!'''