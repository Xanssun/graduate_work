import random
import string
from abc import ABC, abstractmethod
from typing import Union
from uuid import UUID

import aiohttp
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.settings import settings
from db.postgres import get_session
from models.entity import ForeignAccount


class OAuthBase(ABC):
    """
    Абстрактный базовый класс для провайдеров OAuth
    """

    @staticmethod
    @abstractmethod
    def name(*args, **kwargs):
        pass

    @abstractmethod
    def get_authorize_url(self) -> str:
        """
        Возвращает URL для авторизации
        """
        raise NotImplementedError

    @abstractmethod
    async def get_user(self, code: str) -> dict:
        """
        Обмениваем проверочный код на токены, а потом на пользователя
        """
        raise NotImplementedError

    async def create_foreign_account(self, user_id: UUID, data: dict) -> dict:
        """
        Добавляем соц. аккаунт
        """
        statement = select(ForeignAccount).where(
            ForeignAccount.foreign_id == data['id'],
            ForeignAccount.provider == self.name,
        )
        query = await self.db_session.execute(statement)
        soc_account = query.scalars().first()
        if not soc_account:
            soc_account = ForeignAccount(
                user_id=user_id,
                provider=self.name,
                data=data,
                foreign_id=data['id'],
            )
            self.db_session.add(soc_account)
            await self.db_session.commit()
            await self.db_session.refresh(soc_account)
        return soc_account


class YandexOauthService(OAuthBase):
    name = 'yandex'

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session
        self.authorize_url = 'https://oauth.yandex.ru/authorize'
        self.access_token_url = 'https://oauth.yandex.ru/token'
        self.api_base_url = 'https://login.yandex.ru/info'
        self.client_id = settings.yandexclientid
        self.client_secret = settings.yandexclientsecret

    def get_authorize_url(self) -> str:
        return f'{self.authorize_url}?response_type=code&client_id={self.client_id}'

    async def get_user(self, code: str) -> dict:
        session = aiohttp.ClientSession()

        async with session.post(
            self.access_token_url,
            data=f'grant_type=authorization_code&client_id={self.client_id}'
            + f'&client_secret={self.client_secret}&code={code}',
        ) as tokens_response:
            parsed_tokens = await tokens_response.json()
            if parsed_tokens['access_token'] is not None:
                async with session.get(
                    self.api_base_url,
                    headers={
                        'Authorization': f"{parsed_tokens['token_type']} {parsed_tokens['access_token']}"
                    },
                ) as user_response:
                    soc_user = await user_response.json()
                    random_password = ''.join(
                        random.SystemRandom().choice(
                            string.ascii_uppercase + string.digits
                        )
                        for _ in range(32)
                    )
                    return [
                        {
                            'password': random_password,
                            'email': soc_user['default_email']
                            if soc_user['default_email']
                            else f'{random_password}@{random_password}.ru',
                            'first_name': soc_user['first_name'],
                            'last_name': soc_user['last_name'],
                        },
                        soc_user,
                    ]


def get_oauth_service(
    name: str, db_session: AsyncSession = Depends(get_session)
) -> Union[OAuthBase, None]:
    if name == 'yandex':
        return YandexOauthService(db_session=db_session)

    return None
