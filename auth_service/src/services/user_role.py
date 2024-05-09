from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.entity import Privilege, Role, RolePrivilegeMap, User, UserRoleMap


class UserRoleService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create_user_role(self, user_id: UUID, role_id: UUID):
        # check existing user-role with the same title
        dublicate_user_role_stmt = select(UserRoleMap).where(
            UserRoleMap.user_id == user_id, UserRoleMap.role_id == role_id
        )
        dublicate_user_role_query = await self.db_session.execute(
            dublicate_user_role_stmt
        )
        dublicate_user_role = dublicate_user_role_query.scalars().first()
        if dublicate_user_role:
            raise ValueError(
                f'user-Role with user_id {user_id!r} '
                f'and role_id {role_id!r} already exsits!'
            )

        # create user-role
        new_user_role = UserRoleMap(user_id=user_id, role_id=role_id)
        self.db_session.add(new_user_role)
        await self.db_session.commit()
        await self.db_session.refresh(new_user_role)
        return new_user_role

    async def delete_user_role(self, user_role_id: UUID):
        delete_role_stmt = delete(UserRoleMap).where(
            UserRoleMap.id == user_role_id
        )
        await self.db_session.execute(delete_role_stmt)
        await self.db_session.commit()

    async def get_user_roles(self, user_id: UUID):
        user_role_map_stmt = select(UserRoleMap.role_id).where(
            UserRoleMap.user_id == user_id
        )
        roles_stmt = select(Role).join(
            user_role_map_stmt, user_role_map_stmt.c.role_id == Role.id
        )
        roles_query = await self.db_session.execute(roles_stmt)
        roles = roles_query.scalars()

        return roles

    async def get_user_privileges(self, user_id: UUID):
        user_privileges_stmt = (
            select(Privilege)
            .join(
                RolePrivilegeMap, RolePrivilegeMap.privilege_id == Privilege.id
            )
            .join(UserRoleMap, UserRoleMap.role_id == RolePrivilegeMap.role_id)
            .join(User, User.id == UserRoleMap.user_id)
        )

        user_privileges_query = await self.db_session.execute(
            user_privileges_stmt
        )
        user_privileges = user_privileges_query.scalars()

        return user_privileges


def get_user_role_service(
    db_session: AsyncSession = Depends(get_session),
) -> UserRoleService:
    return UserRoleService(db_session=db_session)
