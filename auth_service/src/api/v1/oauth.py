from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from schemas.entity import UserInDB
from services.auth import AuthService, get_auth_service
from services.oauth import OAuthBase, get_oauth_service

router = APIRouter()


@router.get(
    '/signin_{name}',
    summary='Регистрация пользователя через соцсеть',
    description='Регистрация пользователя через соцсеть',
)
async def signin_oauth(
    request: Request,
    name: str,
    oauth_service: OAuthBase = Depends(get_oauth_service),
):
    if oauth_service is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Oauth provider not found'
        )
    return {'redirect_url': oauth_service.get_authorize_url()}
    # return RedirectResponse(url=oauth_service.get_authorize_url())


@router.get(
    '/callback_signin_{name}',
    summary='Обмен кода на токен',
    description='Обмен кода на токен',
)
async def signin_oauth_callback(
    request: Request,
    response: Response,
    name: str,
    code: str = Query(),
    response_model=UserInDB,
    oauth_service: OAuthBase = Depends(get_oauth_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    if oauth_service is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Oauth provider not found'
        )

    foreign_user, data = await oauth_service.get_user(code)
    if not foreign_user:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Something wrong',
        )
    print(f'foreign_user = {foreign_user}')
    user = await auth_service.signup(foreign_user)

    if user is None:
        print(f"\n\nby email = {foreign_user['email']}\n\n")
        user = await auth_service.get_user_by_email(foreign_user['email'])
    print(f'!!!user = {user} \n\n\n')
    print(f'data = {data} \n\n\n')
    await oauth_service.create_foreign_account(user.id, data)

    tokens = await auth_service.signin(
        foreign_user['email'], foreign_user['password'], False
    )
    if not tokens:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Wrong email or password',
        )
    response.headers['X-Access-Token'] = tokens['token']
    response.headers['X-Refresh-Token'] = tokens['refresh_token']

    return tokens['user']
