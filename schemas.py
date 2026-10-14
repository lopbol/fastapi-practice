from pydantic import BaseModel, Field
from datetime import datetime

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=0, le=150)
    email: str = "Не указан"
    
    model_config = {"extra": "forbid"}

class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True