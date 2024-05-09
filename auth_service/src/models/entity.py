import logging
import random
import string
import uuid
from datetime import datetime, timedelta

import jwt
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import check_password_hash, generate_password_hash

from core.settings import settings
from db.postgres import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(
        self, email: str, password: str, first_name: str, last_name: str
    ) -> None:
        self.email = email
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.email}>'


class ForeignAccount(Base):
    __tablename__ = 'foreign_accounts'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    provider = Column(String(50), nullable=False)
    data = Column(JSONB)
    foreign_id = Column(String(255), nullable=False)
    __table_args__ = (
        UniqueConstraint(
            'provider', 'foreign_id', name='provider_foreign_id_unique_idx'
        ),
    )


class Token:
    def __init__(
        self, user_id: int = None, token: str = None, role: list[str] = None
    ):
        if token:
            try:
                decoded = jwt.decode(
                    token,
                    settings.auth_secret,
                    algorithms=['HS256'],
                )
            except Exception as error:
                logging.error(f'Smth wrong with token = {error}')
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
        else:
            self.user_id = user_id
            self.role = role
            expires = datetime.now() + timedelta(
                seconds=settings.auth_token_lifetime
            )
            self.expires = expires.strftime('%Y-%m-%d %H:%M:%S')
            self.role = role
            self.token = self.create_token()

    def create_token(self) -> str:
        return jwt.encode(
            {
                'user_id': str(self.user_id),
                'expires': self.expires,
                'role': self.role,
            },
            settings.auth_secret,
            algorithm='HS256',
        )

    def is_expired(self) -> bool:
        if self.expires >= datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
            return False
        return True

    def __repr__(self) -> str:
        return f"<Token {self.user_id}, roles = {', '.join(self.role)}, expires = {self.expires}>"


class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    expires = Column(DateTime, default=datetime.utcnow)
    refresh_token = Column(String(250))
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    def __init__(
        self, user_id: str, expires: datetime = None, refresh_token: str = None
    ):
        self.expires = expires
        self.refresh_token = refresh_token
        self.user_id = user_id

    def regenerate(self):
        self.refresh_token = ''.join(
            random.SystemRandom().choice(
                string.ascii_uppercase + string.digits
            )
            for _ in range(settings.auth_refresh_token_length)
        )
        self.expires = datetime.now() + timedelta(
            seconds=settings.auth_refresh_token_lifetime
        )

    def __repr__(self) -> str:
        return f'<RefreshToken {self.refresh_token} expires { self.expires }>'


class UserAuthHistory(Base):
    __tablename__ = 'user_auth_history'

    date = Column(DateTime, default=datetime.utcnow, primary_key=True)
    action = Column(String(250))
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    __table_args__ = {
        'postgresql_partition_by': 'RANGE (date)',
    }

    def __init__(self, action, user_id):
        self.action = action
        self.user_id = user_id

    @staticmethod
    async def create_partition_table_if_not_exists(
        db_session: AsyncSession,
    ) -> None:
        """creating partition by month"""
        current_moment = datetime.now()
        current_year = current_moment.year
        current_month = current_moment.month

        month_first_day = f'{current_year}-{current_month:02d}-01'
        if current_month == 12:
            next_month_first_day = f'{current_year + 1}-01-01'
        else:
            next_month_first_day = (
                f'{current_year}-{(current_month + 1):02d}-01'
            )

        query = text(
            f"""CREATE TABLE IF NOT EXISTS "user_auth_history_{current_year}_{current_month}" \
                PARTITION OF "user_auth_history" FOR VALUES \
                FROM ('{month_first_day} 00:00:00') TO ('{next_month_first_day} 23:59:59');"""
        )
        print(query)
        await db_session.execute(query)


class Role(Base):
    __tablename__ = 'roles'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    title = Column(String(250))

    def __init__(self, title):
        self.title = title


class Privilege(Base):
    __tablename__ = 'privileges'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    title = Column(String(250))
    name = Column(String(250))

    def __init__(self, title, name):
        self.title = title
        self.name = name


class RolePrivilegeMap(Base):
    __tablename__ = 'role_privilege_maps'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    privilege_id = Column(
        UUID(as_uuid=True), ForeignKey('privileges.id'), nullable=False
    )
    role_id = Column(
        UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False
    )


class UserRoleMap(Base):
    __tablename__ = 'user_role_maps'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    role_id = Column(
        UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False
    )
    __table_args__ = (
        UniqueConstraint(
            'user_id', 'role_id', name='user_role_maps_unique_idx'
        ),
    )
