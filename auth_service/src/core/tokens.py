import http
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import (
    APIKeyHeader,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from core.settings import settings
from models.entity import Token
from services.auth import AuthService, get_auth_service


class AccessBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(
            request
        )
        if not credentials:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail='Invalid authorization code.',
            )
        if not credentials.scheme == 'Bearer':
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail='Only Bearer token might be accepted',
            )

        decoded_token = self._parse_token(credentials.credentials)
        if not decoded_token:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail='Invalid or expired token.',
            )
        return decoded_token

    @staticmethod
    def _parse_token(jwt_token: str) -> Optional[dict]:
        token = Token(token=jwt_token)
        if not token.is_expired():
            return token
        return None


security_access_token = AccessBearer()


class AccessBearerAdmin(AccessBearer):
    @staticmethod
    def _parse_token(jwt_token: str) -> Optional[dict]:
        token = Token(token=jwt_token)
        if not token.is_expired() and settings.admin_role_title in token.role:
            return token
        return None


security_access_token_admin = AccessBearerAdmin()


async def security_refresh_token(
    refresh_token: str = Depends(APIKeyHeader(name='refresh_token')),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Получаем и проверяем рефреш токен, что не в отозванных
    """
    active_refresh_token = await auth_service.get_refresh_token(refresh_token)
    if not active_refresh_token:
        raise HTTPException(
            status_code=http.HTTPStatus.FORBIDDEN,
            detail='Invalid or expired refresh token.',
        )
    return active_refresh_token
