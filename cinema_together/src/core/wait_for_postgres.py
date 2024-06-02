import logging
import sys
from time import sleep

import psycopg2
from config import Settings

sys.path.insert(0, '/opt/app')
logger = logging.getLogger(__name__)


def wait_for_postgres(pg_conn_data):
    tries = 0
    sleep_time = 1
    factor = 2
    border_sleep_time = 10
    logger.info('Run wait_for_postgres')
    while True:
        try:
            tries += 1
            logger.info(f'Retrying... {tries}')
            psycopg2.connect(**pg_conn_data)
            break
        except Exception as e:
            logger.error(str(e))
            sleep_time = min(sleep_time * 2**factor, border_sleep_time)

            sleep(sleep_time)


if __name__ == '__main__':
    settings = Settings()

    pg_conn_data = {
        'user': settings.kino_db_user,
        'password': settings.kino_db_password,
        'host': settings.kino_db_host,
        'port': settings.kino_db_port,
        'dbname': settings.kino_db_name,
    }

    wait_for_postgres(pg_conn_data)
    logger.info('Postgres is ready!')
