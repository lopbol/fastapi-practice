from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

# Регистрация
class UserRegister(BaseModel):
    email: EmailStr                     # ← проверяет формат email
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=0, le=150)
    password: str = Field(min_length=6, max_length=100)    # ← сырой пароль
    
    model_config = {"extra": "forbid"}

# Логин
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Ответ (без пароля!)
class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    age: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

#обновление пользователя 
class UpdateUser(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    age: int | None = Field(None, ge=0, le=150)
    model_config = {"extra": "forbid"}

class ExerciseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    muscle_group: str = Field(min_length=1, max_length=200)

class ExerciseResponse(BaseModel):
    id: int
    name: str
    muscle_group: str
    class Config:
        from_attributes = True

class WorkoutSetCreate(BaseModel):
    weight: float
    reps: int
    exercise_id: int

class WorkoutSetResponseWithExercise(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class WorkoutSetResponse(BaseModel):
    id: int
    weight: float
    reps: int
    date: datetime
    exercise_id: int
    user_id: int
    exercise: WorkoutSetResponseWithExercise
    class Config:
        from_attributes = True