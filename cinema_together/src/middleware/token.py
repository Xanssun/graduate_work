import http
import logging
from datetime import datetime
from typing import Optional

import jwt
from core.config import settings
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class Token:
    def __init__(self, token: str):
        if token:
            try:
                decoded = jwt.decode(
                    token, settings.auth_secret, algorithms=['HS256']
                )
            except Exception as error:
                logging.error(f'Something wrong with token = {error}')
                decoded = {}
            if (
                decoded.get('user_id')
                and decoded.get('role')
                and decoded.get('expires')
            ):
                self.user_id = decoded['user_id']
                self.expires = decoded['expires']
                self.role = decoded['role']
                self.token = token
            else:
                self.user_id = 'invalid_token'
                self.expires = '0000-00-00 00:00:00'
                self.role = []
                self.token = token

    def is_expired(self) -> bool:
        if self.expires >= datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
            return False
        return True

    def __repr__(self) -> str:
        return f"<Token {self.user_id}, roles = {', '.join(self.role)}, expires = {self.expires}>"

class AccessBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[dict]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == 'Bearer':
                raise HTTPException(
                    status_code=http.HTTPStatus.UNAUTHORIZED,
                    detail='Only Bearer token might be accepted',
                )
            print(credentials.credentials)
            decoded_token = self._parse_token(credentials.credentials)
            if decoded_token:
                return decoded_token
            else:
                raise HTTPException(
                    status_code=http.HTTPStatus.UNAUTHORIZED,
                    detail='Token is expired or invalid',
                )
        raise HTTPException(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            detail='Not authenticated',
        )

    @staticmethod
    def _parse_token(jwt_token: str) -> Optional[dict]:
        token = Token(token=jwt_token)
        print(token)
        if not token.is_expired():
            return token
        return None

security_access_token = AccessBearer()