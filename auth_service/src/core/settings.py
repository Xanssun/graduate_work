import logging

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = 'auth'
    db_name: str = 'movies_database'
    db_user: str = 'app'
    db_password: str = 'emptystring'
    db_host: str = '127.0.0.1'
    db_port: str = '5432'

    redis_host: str = '127.0.0.1'
    redis_port: int = 6379

    auth_api_host: str = '0.0.0.0'
    auth_api_port: int = 8002

    auth_db_name: str = 'auth_database'
    auth_db_user: str = 'app'
    auth_db_password: str = 'emptystring'
    auth_db_host: str = '127.0.0.1'
    auth_db_port: str = '5432'

    es_host: str = '127.0.0.1'
    es_port: str = '9200'

    with_jaeger: bool = False
    jaeger_host: str = '0.0.0.0'
    jaeger_port: int = 6831

    auth_token_lifetime: int = 360
    auth_refresh_token_lifetime: int = 3600
    auth_refresh_token_length: int = 32
    auth_secret: str = 'privedmedved'

    log_level: int = logging.DEBUG

    admin_login: str = 'admin'
    admin_email: str = 'admin@mail.ru'
    admin_password: str = 'admin'

    admin_role_title: str = 'admin'
    simple_role_title: str = 'visitor'
    subscription_role_title: str = 'subscription'

    max_requests_per_minute: int = 10

    yandexclientid: str = '5c2105e6f04147df9ce4861c7a996025'
    yandexclientsecret: str = 'c836c696aa5347149dc05e7dc396dbf2'

    is_debug: bool = False


settings = Settings()
