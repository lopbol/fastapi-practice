import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from database import Base, get_db
from main import app

# 1. Создаём БД в памяти (каждый раз чистую)
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = async_sessionmaker(class_=AsyncSession, expire_on_commit=False, bind=engine)

# 2. Фикстура, которая создаёт таблицы перед тестом и удаляет после
@pytest_asyncio.fixture(scope="function")
async def db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
# 3. Фикстура клиента (подменяем зависимость get_db)
@pytest_asyncio.fixture(scope="function")
async def client(db):
    def override_get_db():
            yield db
    
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

# 4. Фикстура для получения токена (создаёт юзера и логинится)
@pytest_asyncio.fixture(scope="function")
async def auth_token(client):
    # Регистрация
    await client.post("/register", json={
        "email": "test@example.com",
        "name": "Test User",
        "age": 25,
        "password": "password123"
    })
    # Логин
    response = await client.post("/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = response.json()["access_token"]
    return token