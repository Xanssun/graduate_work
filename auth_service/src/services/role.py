from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.entity import Role


class RoleService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def get_all_roles(self):
        """Get all roles from Database"""
        roles_stmt = select(Role)
        roles_query = await self.db_session.execute(roles_stmt)
        roles = roles_query.scalars()
        return roles

    async def create_role(self, title):
        # check existing role with the same title
        dublicate_role = await self.get_role(title)
        if dublicate_role:
            raise ValueError(f'Role with title {title!r} already exsits!')

        # create role
        new_role = Role(title=title)
        self.db_session.add(new_role)
        await self.db_session.commit()
        await self.db_session.refresh(new_role)
        return new_role

    async def update_role(self, role_id: UUID, title):
        # check existing role with the same title
        dublicate_role = await self.get_role(title)
        if dublicate_role:
            raise ValueError(f'Role with title {title!r} already exists!')

        # update role
        role_to_update_stmt = select(Role).where(Role.id == role_id)
        role_to_update_query = await self.db_session.execute(
            role_to_update_stmt
        )  # noqa
        role_to_update = role_to_update_query.scalar_one()

        role_to_update.title = title

        await self.db_session.commit()
        await self.db_session.refresh(role_to_update)
        return role_to_update

    async def delete_role(self, role_id: UUID):
        delete_role_stmt = delete(Role).where(Role.id == role_id)
        await self.db_session.execute(delete_role_stmt)
        await self.db_session.commit()

    async def get_role(self, title: str):
        role_stmt = select(Role).where(Role.title == title)
        role_query = await self.db_session.execute(role_stmt)
        return role_query.scalars().first()


def get_role_service(
    db_session: AsyncSession = Depends(get_session),
) -> RoleService:
    return RoleService(db_session=db_session)
