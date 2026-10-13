import sqlite3

conn = sqlite3.connect("test_users.db")
cursor = conn.cursor()
print("сортировка")
cursor.execute("SELECT * FROM users ORDER BY age DESC")
conn.commit()
for row in cursor.fetchall():
    print(row)
print("фильтр")
cursor.execute("SELECT * FROM users WHERE age > 25")
conn.commit()
for row in cursor.fetchall():
    print(row)
print("ограничение")
cursor.execute("SELECT * FROM users LIMIT 2")
conn.commit()
for row in cursor.fetchall():
    print(row)
print("средний возраст")
cursor.execute("SELECT AVG(age) FROM users")
for row in cursor.fetchall( ):
    print(row)

print("диапазон")
cursor.execute("SELECT name, age FROM users WHERE age BETWEEN 20 AND 30")
conn.commit()
for row in cursor.fetchall():
    print(row)

conn.close()