from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel, Field

app = FastAPI()

users_db = {}
next_id = 1

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=0, le=150)
    email: str = "не указан"

class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    email: str

# READ ALL
@app.get("/users", response_model=list[UserResponse])
def get_users():
    return list(users_db.values())

# READ ONE
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return users_db[user_id]

# CREATE
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    global next_id
    user_id = next_id
    next_id += 1
    users_db[user_id] = {
        "id": user_id,
        "name": user.name,
        "age": user.age,
        "email": user.email,
    }
    return users_db[user_id]

# UPDATE
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    users_db[user_id] = {
        "id": user_id,
        "name": user.name,
        "age": user.age,
        "email": user.email,
    }
    return users_db[user_id]

# DELETE
@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    del users_db[user_id]
    return None

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)