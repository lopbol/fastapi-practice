import sqlite3

conn = sqlite3.connect("test_users.db")
cursor = conn.cursor()

# 1. Создать таблицу
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        email TEXT
    )
""")

# 2. Вставить 3 пользователя
cursor.execute("INSERT INTO users (name, age, email) VALUES (?, ?, ?)",
               ("Аня", 25, "anya@mail.ru"))
cursor.execute("INSERT INTO users (name, age, email) VALUES (?, ?, ?)",
               ("Борис", 30, "boris@mail.ru"))
cursor.execute("INSERT INTO users (name, age, email) VALUES (?, ?, ?)",
               ("Вика", 22, "vika@mail.ru"))
conn.commit()

# 3. Прочитать всех
cursor.execute("SELECT * FROM users")
print("Все пользователи:")
for row in cursor.fetchall():
    print(row)

# 4. Прочитать одного
cursor.execute("SELECT * FROM users WHERE id = ?", (2,))
print("\nПользователь id=2:")
print(cursor.fetchone())

# 5. Обновить
cursor.execute("UPDATE users SET age = ? WHERE name = ?", (31, "Борис"))
conn.commit()

# 6. Проверить обновление
cursor.execute("SELECT * FROM users WHERE name = ?", ("Борис",))
print("\nПосле обновления:")
print(cursor.fetchone())

# 7. Удалить
cursor.execute("DELETE FROM users WHERE name = ?", ("Вика",))
conn.commit()

# 8. Посчитать
cursor.execute("SELECT COUNT(*) FROM users")
print("\nОсталось пользователей:", cursor.fetchone()[0])

conn.close()