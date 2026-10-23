import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

# 1. Создаём БД в памяти (каждый раз чистую)
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Важно для SQLite в памяти
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Фикстура, которая создаёт таблицы перед тестом и удаляет после
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    try:
        db_session = TestingSessionLocal()
        yield db_session
    finally:
        db_session.close()
        Base.metadata.drop_all(bind=engine)

# 3. Фикстура клиента (подменяем зависимость get_db)
@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

# 4. Фикстура для получения токена (создаёт юзера и логинится)
@pytest.fixture(scope="function")
def auth_token(client):
    # Регистрация
    client.post("/register", json={
        "email": "test@example.com",
        "name": "Test User",
        "age": 25,
        "password": "password123"
    })
    # Логин
    response = client.post("/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = response.json()["access_token"]
    return token