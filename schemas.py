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