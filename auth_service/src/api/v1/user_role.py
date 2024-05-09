from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from core.tokens import security_access_token_admin
from models.entity import Token
from schemas.entity import Privilege as PrivilegeResponseSchema
from schemas.entity import Role as RoleResponseShema
from schemas.entity import UserRole as UserRoleResponseShema
from schemas.entity import UserRoleMap
from services.user_role import UserRoleService, get_user_role_service

router = APIRouter()


@router.post(
    '/',
    summary='Создать связь Пользователь-Роль',
    response_model=UserRoleResponseShema,
    description='Создать роль',
    status_code=HTTPStatus.CREATED,
)
async def create_role(
    user_role_map: UserRoleMap,
    token: Annotated[Token, Depends(security_access_token_admin)],
    user_role_service: UserRoleService = Depends(get_user_role_service),
):
    args = jsonable_encoder(user_role_map)
    new_user_role = await user_role_service.create_user_role(
        args['user_id'], args['role_id']
    )
    new_user_role = UserRoleResponseShema(
        id=new_user_role.id,
        user_id=new_user_role.user_id,
        role_id=new_user_role.role_id,
    )
    return new_user_role


@router.delete(
    '/{user_role_id}',
    summary='Удалить связь Пользователь-Роль',
    response_model=None,
    description='Удалить связь Пользователь-Роль',
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_role(
    user_role_id: UUID,
    token: Annotated[Token, Depends(security_access_token_admin)],
    user_role_service: UserRoleService = Depends(get_user_role_service),
):  # noqa

    await user_role_service.delete_user_role(user_role_id)


@router.get(
    '/{user_id}',
    summary='Получить все роли пользователя',
    response_model=list[RoleResponseShema],
    description='Получить все роли пользователя',
    status_code=HTTPStatus.OK,
)
async def get_user_roles(
    user_id: UUID,
    user_role_service: UserRoleService = Depends(get_user_role_service),
):  # noqa

    roles = await user_role_service.get_user_roles(user_id)
    roles = {RoleResponseShema(id=role.id, title=role.title) for role in roles}

    roles = list(roles)
    return roles


@router.get(
    '/user_privileges/{user_id}',
    summary='Получить все права пользователя',
    response_model=list[PrivilegeResponseSchema],
    description='Получить все права пользователя',
    status_code=HTTPStatus.OK,
)
async def get_user_privileges(
    user_id: UUID,
    token: Annotated[Token, Depends(security_access_token_admin)],
    user_role_service: UserRoleService = Depends(get_user_role_service),
):  # noqa

    privileges = await user_role_service.get_user_privileges(user_id)
    privileges = [
        PrivilegeResponseSchema(
            id=privilege.id, title=privilege.title, name=privilege.name
        )
        for privilege in privileges
    ]
    return privileges
