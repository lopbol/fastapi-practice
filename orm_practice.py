from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    age = Column(Integer)
    email = Column(String(100), default="Не указан")

DATABASE_URL = "sqlite:///orm_users.db"
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind = engine, autoflush=False, autocommit=False)

Base.metadata.create_all(bind=engine)

db = SessionLocal()

user1 = User(name="Настя", age = 19, email = "ahomuuuutova@gmail.com")
user2 = User(name="Илья", age = 20, email = "ilia47234@mail.ru")
db.add(user1)
db.add(user2)
db.commit()
db.refresh(user1)
db.refresh(user2)

print(f"Созданы: {user1.id} - {user1.name}, email={user1.email}")
print(f"Созданы: {user2.id} - {user2.name}, email={user2.email}")

all_users = db.query(User).all()
print("\nВсе пользователи:")
for u in all_users:
    print(f"{u.id}: {u.name}, {u.age}, {u.email}")

user = db.query(User).filter(User.id == 1).first()
print(f"\nПользователь с id=1:{user.name}")


user.age = 20
db.commit()
db.refresh(user)
print(f"\nПосле обновления: {user.name}, {user.age}")

db.delete(user2)
db.commit()

count = db.query(User).count()

print(f"\nОсталось: {count}")

db.close()
