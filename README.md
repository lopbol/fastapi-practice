# FastAPI Practice

Учебный проект: REST API на FastAPI с аутентификацией.

## Стек технологий

- **FastAPI** — веб-фреймворк
- **SQLAlchemy** — ORM
- **SQLite** — база данных
- **Pydantic** — валидация данных
- **passlib + bcrypt** — хеширование паролей
- **Uvicorn** — ASGI-сервер

## Структура проекта
.
├── main.py # FastAPI app + роуты
├── database.py # engine, SessionLocal, Base, get_db
├── models.py # SQLAlchemy-модели
├── schemas.py # Pydantic-схемы
├── security.py # хеширование паролей
├── requirements.txt # зависимости
└── README.md

text

## Установка

```bash
pip install -r requirements.txt
Запуск
bash
uvicorn main:app --reload
Сервер: http://127.0.0.1:8000
Swagger UI: http://127.0.0.1:8000/docs

Эндпоинты
Регистрация
POST /register

json
{
  "email": "anya@mail.ru",
  "name": "Аня",
  "age": 25,
  "password": "qwerty123"
}
Ответ: 201 Created

json
{
  "id": 1,
  "email": "anya@mail.ru",
  "name": "Аня",
  "age": 25,
  "created_at": "2026-10-14T21:45:00"
}
Логин
POST /login

json
{
  "email": "anya@mail.ru",
  "password": "qwerty123"
}
Ответ: 200 OK

Безопасность
Пароли хешируются через bcrypt (с солью)

Пароль никогда не хранится и не возвращается в открытом виде

При неверном email или пароле возвращается одинаковое сообщение (чтобы нельзя было выяснить, какие email зарегистрированы)

### Обновление профиля

`PATCH /users/me` (требует токен)

```json
{
  "name": "Новое имя",
  "age": 30
}
Все поля опциональные — обновляются только присланные.

Удаление аккаунта
DELETE /users/me (требует токен)

Возвращает 204 No Content. После удаления токен становится невалидным.