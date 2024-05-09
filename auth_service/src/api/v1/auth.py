from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.encoders import jsonable_encoder

from core.tokens import security_access_token, security_refresh_token
from models.entity import RefreshToken, Token
from schemas.entity import (
    AuthHistory,
    ChangeCredentials,
    HistoryResult,
    Result,
    UserCreate,
    UserInDB,
    UserSignIn,
)
from services.auth import AuthService, get_auth_service
from validators.validate_email_and_password import validate_email_and_password

router = APIRouter()


@router.post(
    '/signup',
    response_model=UserInDB,
    status_code=HTTPStatus.CREATED,
    summary='Регистрация пользователя',
    description='Регистрация пользователя',
)
async def signup(
    user_create: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserInDB:
    args = jsonable_encoder(user_create)
    validate_email_and_password(args['email'], args['password'])
    user = await auth_service.signup(args=args)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Already exists user with such email',
        )
    return user


@router.post(
    '/signin',
    response_model=UserInDB,
    status_code=HTTPStatus.CREATED,
    summary='Вход пользователя',
    description='Вход пользователя',
)
async def signin(
    response: Response,
    user_signin: UserSignIn,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserInDB:
    args = jsonable_encoder(user_signin)
    validate_email_and_password(args['email'], args['password'])
    tokens = await auth_service.signin(args['email'], args['password'])
    if not tokens:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Wrong email or password',
        )
    #    response.set_cookie(key='token', value=tokens['token'], httponly=True)
    #    response.set_cookie(
    #        key='refresh_token', value=tokens['refresh_token'], httponly=True
    #    )
    response.headers['X-Access-Token'] = tokens['token']
    response.headers['X-Refresh-Token'] = tokens['refresh_token']

    return tokens['user']


@router.post(
    '/refresh_token',
    response_model=UserInDB,
    status_code=HTTPStatus.OK,
    summary='Обновить токен',
    description='Обновить токен',
)
async def refresh_token(
    response: Response,
    refresh_token: Annotated[RefreshToken, Depends(security_refresh_token)],
    auth_service: AuthService = Depends(get_auth_service),
) -> UserInDB:
    tokens = await auth_service.refresh_token(refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Unauthorized',
        )
    response.headers['X-Access-Token'] = tokens['token']
    response.headers['X-Refresh-Token'] = tokens['refresh_token']

    return tokens['user']


@router.post(
    '/change_credentials',
    response_model=UserInDB,
    status_code=HTTPStatus.OK,
    summary='Изменение логина или пароля',
    description='Изменение логина или пароля',
)
async def change_credentials(
    refresh_token: Annotated[RefreshToken, Depends(security_refresh_token)],
    credentials: ChangeCredentials,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserInDB:
    args = jsonable_encoder(credentials)
    validate_email_and_password(args['email'], args['password'], False)
    updated_user = await auth_service.change_credentials(
        refresh_token,
        args,
    )
    if not updated_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Already exists user with such email',
        )
    return updated_user


@router.post(
    '/history',
    response_model=list[HistoryResult],
    status_code=HTTPStatus.OK,
    summary='Получение пользователем своей истории входов в аккаунт',
    description='Получение пользователем своей истории входов в аккаунт',
)
async def history(
    token: Annotated[Token, Depends(security_access_token)],
    auth_history: AuthHistory,
    page: Annotated[int, Query(title='Номер страницы', ge=1)] = 1,
    size: Annotated[int, Query(title='Размер страницы', ge=1, le=500)] = 100,
    auth_service: AuthService = Depends(get_auth_service),
) -> list[HistoryResult]:
    args = jsonable_encoder(auth_history)
    history = await auth_service.auth_history(
        token=token, start=args['start'], end=args['end'], page=page, size=size
    )
    return [HistoryResult(date=obj.date, action=obj.action) for obj in history]


@router.post(
    '/logout',
    response_model=Result,
    status_code=HTTPStatus.OK,
    summary='Выход',
    description='Выход',
)
async def logout(
    refresh_token: Annotated[RefreshToken, Depends(security_refresh_token)],
    auth_service: AuthService = Depends(get_auth_service),
) -> Result:
    result = await auth_service.logout(refresh_token=refresh_token)
    if result:
        return Result(success=True)
    return Result(success=False)
