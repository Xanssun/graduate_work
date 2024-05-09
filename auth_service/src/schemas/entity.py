from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class Token(BaseModel):
    token: str


# регистрация пользователя
class UserCreate(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str


class UserInDB(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class Result(BaseModel):
    success: bool


# вход пользователя в аккаунт (обмен логина и пароля на пару токенов: JWT-access токен и refresh токен);
class UserSignIn(BaseModel):
    email: str
    password: str


class Tokens(Token):
    token: str
    refresh_token: str
    expires: datetime

    class Config:
        orm_mode = True


# обновление access-токена;
class RefreshToken(BaseModel):
    refresh_token: str


# изменение логина или пароля
class ChangeCredentials(BaseModel):
    email: str = None
    password: str = None
    first_name: str = None
    last_name: str = None


# получение пользователем своей истории входов в аккаунт;
class AuthHistory(BaseModel):
    start: date
    end: date


class HistoryResult(BaseModel):
    date: datetime
    action: str


# работа с ролями
class Role(BaseModel):
    id: UUID
    title: str


class UserRole(BaseModel):
    id: UUID
    user_id: UUID
    role_id: UUID


class UserRoleMap(BaseModel):
    user_id: UUID
    role_id: UUID


class Privilege(BaseModel):
    id: UUID
    title: str
    name: str
