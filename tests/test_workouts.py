import pytest

@pytest.mark.asyncio
async def test_create_exercise(client, auth_token):
    '''тест успешное создание упражнения'''
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.post("/exercise", headers = headers, json={
        "name": "string",
        "muscle_group": "string"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "string"
    assert "id" in data
    assert data["muscle_group"] == "string"

@pytest.mark.asyncio
async def test_create_workout(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    '''тест создание подхода'''
    start = await client.post("/exercise", headers=headers, json={
        "name": "string",
        "muscle_group": "string"
    })
    exercise_id = start.json()["id"]
    response = await client.post("/workouts", headers=headers, json={
        "weight": 50,
        'reps': 3,
        'exercise_id': exercise_id
    })
    assert response.status_code == 201
    data = response.json()
    assert data["weight"] == 50
    assert data["reps"] == 3
    assert data["user_id"] == 1
    assert data["exercise_id"] == exercise_id

@pytest.mark.asyncio
async def test_create_workout_no_exercise(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    '''тест создания подхода к несуществующему упражнению'''
    response = await client.post("/workouts", headers=headers, json={
        "weight": 50,
        'reps': 3,
        'exercise_id': 999
    })
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_stats(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    '''тест получение статистики'''
    ex = await client.post("/exercise", headers=headers, json={
        "name": "babochka",
        "muscle_group": "grud"
    })
    exercise_id = ex.json()["id"]
    w1 = await client.post("/workouts", headers=headers, json={
        "weight": 50,
        'reps': 8,
        'exercise_id': exercise_id
    })
    w2 = await client.post("/workouts", headers=headers, json={
        "weight": 70,
        'reps': 6,
        'exercise_id': exercise_id
    })
    response = await client.get(f"/workouts/stats/{exercise_id}", headers=headers)
    data = response.json()
    assert response.status_code == 200
    assert data["max_weight"]==70
    assert data["total_reps"]==14
    assert data["total_sets"]==2

@pytest.mark.asyncio    
async def test_delete_other_user_workout(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    '''тест Удаление чужого подхода'''
    ex = await client.post("/exercise", headers=headers, json={
        "name": "babochka",
        "muscle_group": "grud"
    })
    exercise_id = ex.json()["id"]
    w1 = await client.post("/workouts", headers=headers, json={
        "weight": 50,
        'reps': 8,
        'exercise_id': exercise_id
    })
    set_id = w1.json()["id"]

    new_users = await client.post("/register", json={
        "email": "i@gmail.com",
        "name": "Илья",
        "age": 25,
        "password": "securep"
        })
    new_users_login = await client.post("/login", json={
        "email": "i@gmail.com",
        "password": "securep"
    })
    access_token = new_users_login.json()["access_token"]

    headers_b = {"Authorization": f"Bearer {access_token}"}
    delete_not_my_workouts = await client.delete(f"/workouts/{set_id}", headers = headers_b)
    assert delete_not_my_workouts.status_code == 403