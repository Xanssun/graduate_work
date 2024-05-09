import re
from http import HTTPStatus

from fastapi import HTTPException


def validate_email_and_password(
    email: str, password: str, required: bool = True
):
    """
    Простенько проверяем почту и пароль
    """
    if email and not re.match(r'^\S+@\S+\.\S+$', email):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Bad email',
        )
    if (
        password and (len(password) > 10 or len(password) < 3)
    ) or not password:
        if required:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Bad password',
            )
    return True
