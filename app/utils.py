import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Request
from datetime import datetime, timedelta
from passlib.context import CryptContext

SECRET_KEY = "ec6595083771d01c640057958f1f0b7738802da2568121fcdd05186d2df1a5bf"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# захэшировать пароль
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# проверить пароль
def check_password(input_pass: str, pass_on_db: str) -> bool:
    return pwd_context.verify(input_pass, pass_on_db)


# создать jwt токен
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


# декодировать jwt токен
def decode_jwt_token(token: str) -> dict:
    decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return decoded_jwt


# получить юзера без пароля в виде словаря из бд / для регистрации
def get_user_from_db_wo_pass(db: list, username: str) -> dict | None:
    for user in db:
        if user["username"] == username:
            new_user = user.copy()
            new_user.pop("password")
            return new_user
    return None


# получить юзера из бд (тоже без пароля) / для входа
def get_user_from_db(db: list, username: str, password: str) -> dict | None:
    for user in db:
        if user["username"] == username and check_password(password, user["password"]):
            new_user = user.copy()
            new_user.pop("password")
            return new_user
    return None


# добавить нового юзера в бд и вернуть его id
def insert_new_user_in_db(db: list, username: str, password: str) -> int:
    hashed_password = hash_password(password)
    new_id = db[-1]["id"] + 1
    db.append({
        "id": new_id,
        "username": username,
        "password": hashed_password,
    })
    return new_id


def token_authenticate_user(request: Request) -> dict | bool:
    token = request.cookies.get("access_token")
    if token:
        try:
            decoded_token = decode_jwt_token(token)
            return decoded_token
        except InvalidTokenError:  # если токен неправильный
            return False
    return False  # если токена нет
