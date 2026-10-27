from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, selectinload
import uvicorn
from sqlalchemy import func 

from database import Base, engine, get_db
from models import UserDB, ExerciseDB, WorkoutSetDB
from schemas import UserRegister, UserLogin, UserResponse, Token, UpdateUser, ExerciseCreate, ExerciseResponse, WorkoutSetCreate, WorkoutSetResponse
from security import hash_password, verify_password, create_access_token, decode_token

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

security = HTTPBearer(scheme_name="JWT")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
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
    result = await db.execute(select(UserDB).where(UserDB.id == int(user_id)))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user

@app.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    # Асинхронный запрос через select()
    result = await db.execute(select(UserDB).where(UserDB.email == user_data.email))
    existing = result.scalars().first()
    
    if existing is not None:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    db_user = UserDB(email=user_data.email,
            name=user_data.name,
            age=user_data.age,
            hashed_password=hash_password(user_data.password)
            )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.post("/login")
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    # 1. Найти пользователя
    result = await db.execute(select(UserDB).where(UserDB.email == credentials.email))
    user = result.scalars().first()
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
async def get_my_workouts(current_user: UserDB = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkoutSetDB).where(WorkoutSetDB.user_id == current_user.id).order_by(WorkoutSetDB.date).options(selectinload(WorkoutSetDB.exercise)))
    workout = result.scalars().all()
    return workout

@app.patch("/users/me", response_model=UserResponse)
async def update(user_data: UpdateUser, current_user: UserDB = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user_data.name is not None:
        current_user.name = user_data.name
    if user_data.age is not None:
        current_user.age = user_data.age
    await db.commit()
    await db.refresh(current_user)
    return current_user

@app.delete("/users/me", status_code=204)
async def delite_me(current_user: UserDB = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await db.delete(current_user)
    await db.commit()
    return None

@app.get("/users/me", response_model=UserResponse)
def get_me(current_user: UserDB = Depends(get_current_user)):
    return current_user

#Ручки дял упражнений
@app.post("/exercise", response_model=ExerciseResponse, status_code=201)
async def create_exercise(exercise_data: ExerciseCreate, current_user: UserDB = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    new_exercise = ExerciseDB(
            name=exercise_data.name,
            muscle_group=exercise_data.muscle_group
            )
    db.add(new_exercise)
    await db.commit()
    await db.refresh(new_exercise)
    return new_exercise

@app.get("/exercise", )
async def get_all_exercise(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ExerciseDB))
    return result.scalars().all()

#Ручки для тренировок
@app.post("/workouts", response_model=WorkoutSetResponse, status_code=201)
async def create_workouts(workouts_data: WorkoutSetCreate, current_user: UserDB = Depends(get_current_user),  db: AsyncSession = Depends(get_db)):
    # 1. Проверяем, есть ли такое упражнение
    result = await db.execute(select(ExerciseDB).where(ExerciseDB.id == workouts_data.exercise_id))
    exercise = result.scalars().first()
    if exercise is None:
        raise HTTPException(status_code=404, detail="Упражнение не найдено")

    # 2. Создаем тренировку
    new_workouts = WorkoutSetDB(
        weight=workouts_data.weight,
        reps=workouts_data.reps,
        exercise_id=workouts_data.exercise_id,
        user_id=current_user.id
    )
    db.add(new_workouts)
    await db.commit()
    
    # 3. Делаем запрос, чтобы подгрузить exercise (связь)
    result = await db.execute(
        select(WorkoutSetDB)
        .where(WorkoutSetDB.id == new_workouts.id)
        .options(selectinload(WorkoutSetDB.exercise))
    )
    return result.scalars().first()
    


@app.get("/workouts/stats/{exercise_id}")
async def get_my_stats(exercise_id: int, current_user: UserDB = Depends(get_current_user),  db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ExerciseDB).where(ExerciseDB.id == exercise_id))
    s = result.scalars().first()
    if s is None:
        raise HTTPException(status_code=404, detail='Упражнение не найдено')
        
    result2 = await db.execute(select(
        func.max(WorkoutSetDB.weight),
        func.count(WorkoutSetDB.id),
        func.sum(WorkoutSetDB.reps)
    ).where(WorkoutSetDB.user_id == current_user.id, WorkoutSetDB.exercise_id == exercise_id))
    
    stats = result2.first() # ✅ .first() без scalars!
    
    return {
        "max_weight": stats[0] if stats[0] is not None else 0,
        "total_sets": stats[1],
        "total_reps": stats[2] if stats[2] is not None else 0
    }

@app.delete("/workouts/{set_id}", status_code=204)
async def delete_my_workout(set_id: int, current_user: UserDB = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkoutSetDB).where(WorkoutSetDB.id==set_id))
    sets = result.scalars().first() # ✅ Добавлен scalars()
    if sets is None:
        raise HTTPException(status_code=404, detail="Подход не найден")
    if sets.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нельзя удалить чужой подход")
    await db.delete(sets)
    await db.commit()
    return None

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
