from asyncio import run as aiorun
from enum import Enum

import typer
from core.settings import settings
from db.postgres import get_session
from services.auth import get_auth_service
from services.role import get_role_service
from services.user_role import get_user_role_service


class Actions(str, Enum):
    superuser = 'superuser'
    roles = 'roles'


def main(
    email: str = typer.Argument(settings.admin_email),
    password: str = typer.Argument(settings.admin_password),
    action: Actions = Actions.superuser,
):
    async def create_admin():
        db = get_session()
        db_session = await db.__anext__()
        role_service = get_role_service(db_session)
        if action == 'roles':
            try:
                ROLES_TO_CREATE = [
                    settings.simple_role_title,
                    settings.admin_role_title,
                    settings.subscription_role_title,
                ]
                for title in ROLES_TO_CREATE:
                    await role_service.create_role(title)
            except ValueError:
                pass
        else:
            auth_service = get_auth_service(db_session)
            user_role_service = get_user_role_service(db_session)
            try:
                new_user = await auth_service.signup(
                    {
                        'first_name': 'User',
                        'last_name': 'Super',
                        'email': email,
                        'password': password,
                    }
                )
                if new_user is None:
                    new_user = await auth_service._get_user_by_email(email)
                admin_role = await role_service.get_role(
                    settings.admin_role_title
                )
                await user_role_service.create_user_role(
                    new_user.id, admin_role.id
                )
            except Exception as e:
                print(e)

    aiorun(create_admin())


if __name__ == '__main__':
    typer.run(main)
