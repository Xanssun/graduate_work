from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from core.tokens import security_access_token_admin
from models.entity import Token
from schemas.entity import Role as RoleResponseShema
from services.role import RoleService, get_role_service

router = APIRouter()


@router.get(
    '/',
    summary='Получить роли',
    response_model=list[RoleResponseShema],
    description='Получить список всех ролей',
    status_code=HTTPStatus.OK,
)
async def get_roles(
    token: Annotated[Token, Depends(security_access_token_admin)],
    role_service: RoleService = Depends(get_role_service),
):
    roles = await role_service.get_all_roles()
    roles = [RoleResponseShema(id=role.id, title=role.title) for role in roles]
    return roles


@router.post(
    '/',
    summary='Создать роль',
    response_model=RoleResponseShema,
    description='Создать роль',
    status_code=HTTPStatus.CREATED,
)
async def create_role(
    title: str,
    token: Annotated[Token, Depends(security_access_token_admin)],
    role_service: RoleService = Depends(get_role_service),
):
    new_role = await role_service.create_role(title)
    new_role = RoleResponseShema(id=new_role.id, title=new_role.title)
    return new_role


@router.put(
    '/{role_id}',
    summary='Обновить роль',
    response_model=RoleResponseShema,
    description='Обновить роль',
    status_code=HTTPStatus.OK,
)
async def update_role(
    role_id: UUID,
    title: str,
    token: Annotated[Token, Depends(security_access_token_admin)],
    role_service: RoleService = Depends(get_role_service),
):
    updated_role = await role_service.update_role(role_id, title)
    updated_role = RoleResponseShema(
        id=updated_role.id, title=updated_role.title
    )
    return updated_role


@router.delete(
    '/{role_id}',
    summary='Удалить роль',
    response_model=None,
    description='Удалить роль',
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_role(
    role_id: UUID,
    token: Annotated[Token, Depends(security_access_token_admin)],
    role_service: RoleService = Depends(get_role_service),
):
    await role_service.delete_role(role_id)
