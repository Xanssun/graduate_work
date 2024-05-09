#!/bin/bash

# src в sys.path
export PYTHONPATH="/opt/app/src"

python3 /opt/app/core/wait_for_postgres.py &&
alembic -c/opt/app/alembic.ini upgrade head &&
python3 /opt/app/fill_db.py --action roles &&
python3 /opt/app/fill_db.py && python3 /opt/app/main.py