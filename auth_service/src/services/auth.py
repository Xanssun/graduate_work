from datetime import datetime
from typing import Union
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash

from core.settings import settings
from db.postgres import get_session
from db.redis import AsyncCacheStorage, get_redis
from models.entity import (
    RefreshToken,
    Role,
    Token,
    User,
    UserAuthHistory,
    UserRoleMap,
)


class AuthService:
    def __init__(
        self, db_session: AsyncSession, tokens_cache: AsyncCacheStorage
    ) -> None:
        self.db_session = db_session
        self.tokens_cache = tokens_cache

    async def signup(self, args: dict) -> Union[User, None]:
        """
        Регистрируем пользователя
        """
        exists_user = await self.get_user_by_email(args['email'])
        if not exists_user:
            user = User(**args)
            self.db_session.add(user)
            await self.db_session.commit()
            await self.db_session.refresh(user)
            await self._create_auth_history(action='signup', user_id=user.id)

            base_role_statement = select(Role).where(
                Role.title == settings.simple_role_title
            )
            base_role_query = await self.db_session.execute(
                base_role_statement
            )
            base_role_obj = base_role_query.scalars().first()

            user_role_map = UserRoleMap(
                user_id=user.id, role_id=base_role_obj.id
            )
            self.db_session.add(user_role_map)
            await self.db_session.commit()
            await self.db_session.refresh(user_role_map)

            return user

    async def signin(
        self, email: str, password: str, check_pass: bool = True
    ) -> Union[dict, None]:
        """
        Авторизация
        """
        user = await self.get_user_by_email(email)
        if user:
            password_ok = user.check_password(password)
            if (check_pass and password_ok) or not check_pass:
                user_id = user.id

                refresh_token = await self._create_refresh_token(
                    user_id=user_id
                )
                await self._create_auth_history(
                    action='signin', user_id=user_id
                )

                user_roles = await self._get_role_title_by_user_id(
                    user_id=user_id
                )
                token = Token(user_id=user_id, role=user_roles)

                return {
                    'user': user,
                    'token': token.token,
                    'refresh_token': refresh_token.refresh_token,
                    'expires': refresh_token.expires.strftime(
                        '%Y-%m-%d %H:%M:%S'
                    ),
                }
            else:
                await self._create_auth_history(
                    action='bad_password', user_id=user.id
                )

    async def refresh_token(self, refresh_token: RefreshToken) -> dict:
        """
        Обновление рефреш токена
        """
        user = await self._get_user_by_id(id=refresh_token.user_id)
        if user:
            new_refresh_token = await self._renew_refresh_token(
                refresh_token=refresh_token
            )
            await self._create_auth_history(
                action='refresh_token', user_id=refresh_token.user_id
            )
            user_roles = await self._get_role_title_by_user_id(
                user_id=refresh_token.user_id
            )
            token = Token(user_id=user.id, role=user_roles)
            return {
                'user': user,
                'token': token.token,
                'refresh_token': new_refresh_token.refresh_token,
                'expires': new_refresh_token.expires.strftime(
                    '%Y-%m-%d %H:%M:%S'
                ),
            }

    async def change_credentials(
        self, refresh_token: RefreshToken, args: dict
    ) -> Union[User, None]:
        """
        Меняем имя, фамилию, логин или пароль
        """

        user = await self._get_user_by_id(refresh_token.user_id)
        if user:
            if args['last_name']:
                user.last_name = args['last_name']
            if args['first_name']:
                user.first_name = args['first_name']

            if args['email']:
                exists_statement = select(User).where(
                    User.email == args['email'], User.id != user.id
                )
                exists_query = await self.db_session.execute(exists_statement)
                exists_obj = exists_query.scalars().first()
                if exists_obj:
                    return None
                user.email = args['email']
            if args['password']:
                user.password = generate_password_hash(args['password'])

            await self.db_session.commit()
            await self.db_session.refresh(user)
            await self._create_auth_history(action='edit', user_id=user.id)
            return user

    async def auth_history(
        self, token: Token, start: str, end: str, page: int, size: int
    ) -> list:
        """
        История авторизаций, изменений данных и других действий пользователя
        """
        statement = (
            select(UserAuthHistory)
            .where(
                UserAuthHistory.user_id == token.user_id,
                UserAuthHistory.date
                >= datetime.strptime(f'{start} 00:00:00', '%Y-%m-%d %H:%M:%S'),
                UserAuthHistory.date
                <= datetime.strptime(f'{end} 23:59:59', '%Y-%m-%d %H:%M:%S'),
            )
            .limit(size)
            .offset((page - 1) * size)
        )
        auth_history_query = await self.db_session.execute(statement)
        objs = auth_history_query.scalars()
        await self._create_auth_history(
            action='history', user_id=token.user_id
        )
        return objs

    async def logout(self, refresh_token: RefreshToken) -> bool:
        """
        Выход
        """
        await self._put_revoked_refresh_token_to_cache(
            refresh_token.refresh_token
        )

        return True

    async def get_refresh_token(
        self, refresh_token: str
    ) -> Union[RefreshToken, None]:
        """
        Проверяем рефреш токен, что не в отозванных и что вообще такой есть
        """
        is_revoked = await self._get_revoked_refresh_token_from_cache(
            refresh_token
        )
        if is_revoked:
            return None

        statement = select(RefreshToken).where(
            RefreshToken.refresh_token == refresh_token,
            RefreshToken.expires >= datetime.now(),
        )
        query = await self.db_session.execute(statement)
        return query.scalars().first()

    async def get_user_by_email(self, email: str) -> Union[User, None]:
        """
        Получаем пользователя по почте
        """
        statement = select(User).where(User.email == email)
        query = await self.db_session.execute(statement)
        return query.scalars().first()

    async def _put_revoked_refresh_token_to_cache(
        self, refresh_token: str
    ) -> None:
        """
        Сохраняем рефреш токен в кеш как отозваный
        """
        await self.tokens_cache.set(refresh_token, '1')

    async def _get_revoked_refresh_token_from_cache(
        self, refresh_token: str
    ) -> bool:
        """
        Проверяем есть ли такой отозванный рефреш токен
        """
        data = await self.tokens_cache.get(refresh_token)
        if data:
            return True
        return False

    async def _create_auth_history(
        self, action: str, user_id: UUID
    ) -> UserAuthHistory:
        """
        Добавляем запись в историю действий пользователя
        """

        await UserAuthHistory.create_partition_table_if_not_exists(
            self.db_session
        )
        history = UserAuthHistory(action=action, user_id=user_id)
        self.db_session.add(history)
        await self.db_session.commit()
        await self.db_session.refresh(history)
        return history

    async def _get_user_by_id(self, id: UUID) -> Union[User, None]:
        """
        Получаем пользователя по id
        """
        statement = select(User).where(User.id == id)
        query = await self.db_session.execute(statement)
        return query.scalars().first()

    async def _get_role_title_by_user_id(
        self, user_id: UUID
    ) -> Union[str, None]:
        """
        Получаем список ролей пользоватля
        """
        statement = (
            select(Role)
            .join(
                UserRoleMap,
                UserRoleMap.role_id == Role.id,
            )
            .where(UserRoleMap.user_id == user_id)
        )
        query = await self.db_session.execute(statement)
        roles = query.scalars()
        return [role.title for role in roles]

    async def _create_refresh_token(self, user_id: UUID) -> RefreshToken:
        """
        Создаем новый refresh_token
        """
        refresh_token = RefreshToken(user_id=user_id)
        refresh_token.regenerate()
        self.db_session.add(refresh_token)
        await self.db_session.commit()
        await self.db_session.refresh(refresh_token)
        return refresh_token

    async def _renew_refresh_token(
        self, refresh_token: RefreshToken
    ) -> RefreshToken:
        """
        Обновление токена (замена существующего)
        """
        refresh_token.regenerate()
        await self.db_session.commit()
        await self.db_session.refresh(refresh_token)
        return refresh_token


def get_auth_service(
    db_session: AsyncSession = Depends(get_session),
    tokens_cache: AsyncCacheStorage = Depends(get_redis),
) -> AuthService:
    return AuthService(db_session=db_session, tokens_cache=tokens_cache)
