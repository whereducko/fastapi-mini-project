from sqlalchemy import create_engine, select, insert, update, delete, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, sessionmaker
from sqlalchemy.exc import DatabaseError

# фейк бд для начала
FAKE_DB = [
    {"id": 1,
     "username": "admin",
     "email": "",
     "password": "$2b$12$nO9sy8igFTuGFkjKyZ7PoOGNMq8kzE5rCzuEoOMKkwRs2B.5H7Xpe",  # admin
     },
    {"id": 2,
     "username": "toha",
     "email": "toha@test.com",
     "password": "$2b$12$g2R.MXVMAv93C3M5fbZ3Bu6g0qVgizHc6TNAtF9BFzY3WE7WMZbnC",  # tohatop123
     },
    {"id": 3,
     "username": "anton111",
     "email": "",
     "password": "$2b$12$kJvE82jHtLlF3g5ig93i6eq63Rnq64jRv73I1TYWSlNZj6Q0JGtDS",  # anton228
     },
    {"id": 4,
     "username": "peter",
     "email": "peter@parker.com",
     "password": "$2b$12$3DlWYfwAtM1Q9FUI9ipnH.fCsYjSz9y1XFn0.OhDdL6s92J9aCg5K",  # peter89$
     },
    {"id": 5,
     "username": "elon123",
     "email": "elon@musk.com",
     "password": "$2b$12$F977pS7/4DZTQ4ySWJTp3O6HH7RYNh3TcrhaB1PDWOAUUOscsTRD6",  # elon928357239musk
     },
]

# указать данные бд postgres
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_NAME = "test"

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
session_hz = sessionmaker(engine)
session = session_hz()
Base = declarative_base()


# модель (таблица) users
class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(nullable=True)


# # создать таблицу
# Base.metadata.create_all(engine)


# функция для вывода информации с бд + пагинация
def get_db_func(limit_count: int, offset_count: int):
    result = session.execute(
        select(Users.id, Users.username, Users.password, Users.email).limit(limit_count).offset(offset_count)
    )
    final_list = list(result.mappings().all())
    if offset_count > 0:
        exists_prev_data = session.execute(
            select(Users.id, Users.username, Users.password, Users.email).limit(1).offset(offset_count - 1)
        )
        start_data = exists_prev_data.mappings().all()
        if len(start_data) >= 1:
            final_list.insert(0, offset_count // 100)
    else:
        final_list.insert(0, 0)
    exists_next_data = session.execute(
        select(Users.id, Users.username, Users.password, Users.email).limit(1).offset(offset_count + 100)
    )
    end_data = exists_next_data.mappings().all()
    if len(end_data) >= 1:
        final_list.append(offset_count // 100 + 2)
    else:
        final_list.append(0)
    return final_list


def get_count_rows_db():
    count = session.execute(select(func.count()).select_from(Users))
    return count.scalar()


def insert_db_func(
        user_id: int,
        user_username: str,
        user_password: str,
        user_email: str
):
    try:
        session.execute(
            insert(Users).values(
                id=user_id,
                username=user_username,
                password=user_password,
                email=user_email,
            )
        )
        session.commit()
    except DatabaseError:
        session.rollback()


def update_db_func(
        user_id: int,
        user_username: str,
        user_password: str,
        user_email: str
):
    try:
        session.execute(
            update(Users).values(
                username=user_username,
                password=user_password,
                email=user_email,
            ).where(Users.id == user_id)
        )
        session.commit()
    except DatabaseError:
        session.rollback()


def delete_user_from_db_func(user_id: int):
    try:
        session.execute(
            delete(Users).where(Users.id == user_id)
        )
        session.commit()
    except DatabaseError:
        session.rollback()
