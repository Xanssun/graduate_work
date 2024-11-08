#!/bin/bash
set -e

psql --username postgres --dbname postgres <<-EOSQL
    CREATE USER $KINO_DB_USER;
    CREATE DATABASE $KINO_DB_NAME;
    ALTER DATABASE $KINO_DB_NAME OWNER TO $KINO_DB_USER;
    GRANT ALL PRIVILEGES ON DATABASE $KINO_DB_NAME TO $KINO_DB_USER;
EOSQL
