from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel, Field

app = FastAPI()

class User(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=0, le=150)
    email: str = "не указан"

@app.post("/users")
def create_user(user: User):
    return {
        "message": "Пользователь создан",
        "user": user,
    }



@app.get("/")
def root():
    return {"message": "Мой первый API"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/hello/{name}")
def hello_name(name: str):
    return {"message": f"привет, {name}"}

@app.get("/square/{number}")
def square(number: int):
    return {"result": number ** 2}

@app.get("/sum/{a}/{b}")
def summ(a: int, b: int):
    return {"result": a+b}
@app.get("/multiply/{a}/{b}")
def multiply(a: int, b: int):
    return {"result": a*b}
@app.get("/divide/{a}/{b}")
def divide(a: int, b: int):
    if b==0:
        raise HTTPException(status_code=400, detail="на ноль делить нельзя")
    return {"result": a/b}
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)