def test_register_user(client):
    """Тест: успешная регистрация"""
    response = client.post("/register", json={
        "email": "anya@mail.ru",
        "name": "Аня",
        "age": 25,
        "password": "securepass"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "anya@mail.ru"
    assert "id" in data
    assert "hashed_password" not in data  # Проверка безопасности!

def test_register_duplicate_email(client):
    """Тест: нельзя зарегистрировать один email дважды"""
    user_data = {
        "email": "anya@mail.ru",
        "name": "Аня",
        "age": 25,
        "password": "securepass"
    }
    client.post("/register", json=user_data)  # Первый раз
    response = client.post("/register", json=user_data)  # Второй раз
    assert response.status_code == 400

def test_get_me(client, auth_token):
    """Тест: получение своего профиля"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_get_me_without_token(client):
    """Тест: без токена доступа нет"""
    response = client.get("/users/me")
    assert response.status_code == 401  # или 401, зависит от версии FastAPI