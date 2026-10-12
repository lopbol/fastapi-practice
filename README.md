# FastAPI Practice

Учебный проект: первый API на FastAPI.

## Установка

```bash
pip install -r requirements.txt
Запуск
bash
uvicorn main:app --reload
Или:

bash
python main.py
Сервер будет доступен на http://127.0.0.1:8000.

Эндпоинты
GET
GET / — приветствие

GET /health — проверка здоровья

GET /hello/{name} — приветствие по имени

GET /square/{number} — квадрат числа

GET /sum/{a}/{b} — сумма

GET /multiply/{a}/{b} — произведение

GET /divide/{a}/{b} — деление (400 при делении на ноль)

POST
POST /users — создать пользователя

Тело запроса:

json
{
  "name": "Аня",
  "age": 25,
  "email": "anya@mail.ru"
}
Документация
Swagger UI: http://127.0.0.1:8000/docs