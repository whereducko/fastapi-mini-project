import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Request, Depends, HTTPException
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
def create_jwt_token(data: dict, type_token: str, expire_hours: int | float) -> str:
    to_encode = data.copy()
    type_t = type_token
    expire = datetime.utcnow() + timedelta(hours=expire_hours)
    to_encode.update({"type": type_t, "exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


# создать jwt access токен
def create_access_token(data: dict) -> str:
    token = create_jwt_token(data, "access", 0.25)
    return token


# создать jwt refresh токен
def create_refresh_token(data: dict) -> str:
    token = create_jwt_token(data, "refresh", 720)
    return token


# декодировать jwt токен
def decode_jwt_token(token: str) -> dict:
    decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return decoded_jwt


# получить юзера из бд | для регистрации и входа
def get_user_from_db(
        db: list,
        username: str,
        password: str | None = None
) -> dict | None:
    if password is None:
        for user in db:
            if user["username"] == username:
                new_user = user.copy()
                new_user.pop("password")
                return new_user
    else:
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


# функция для проверки токена (есть ли токен в куках)
def token_authenticate_user(request: Request) -> dict | bool:
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    if access_token:  # есть ли access_token?
        try:
            decoded_acc_token = decode_jwt_token(access_token)
            return decoded_acc_token
        except InvalidTokenError:
            return False
    if refresh_token:  # есть ли refresh_token?
        try:
            decoded_ref_token = decode_jwt_token(refresh_token)
            return decoded_ref_token
        except InvalidTokenError:
            return False
    return False


# функция для проверки токенов (refresh и access)
def full_auth_check(is_auth: dict | bool = Depends(token_authenticate_user)):
    if not is_auth:  # если нету, то перенаправляем на /login
        raise HTTPException(
            status_code=302,
            headers={"Location": "/login"},
        )
    if is_auth.get("type") == "refresh":  # если refresh, то перенаправляем на /refresh, чтобы создать access
        raise HTTPException(
            status_code=302,
            headers={"Location": "/refresh"},
        )
    return is_auth  # в ином случае возвращаем токен (ожидается access токен)
