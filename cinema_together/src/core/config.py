# from logging import config as logging_config

from pydantic_settings import BaseSettings

# from core.logger import LOGGING

# Применяем настройки логирования
# logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):

    kino_api_host: str = '0.0.0.0'
    kino_api_port: int = 8005

    kino_db_name: str = 'kino_database'
    kino_db_user: str = 'app'
    kino_db_password: str = '123qwe'
    kino_db_host: str = '127.0.0.1'
    kino_db_port: str = '5432'


settings = Settings()
