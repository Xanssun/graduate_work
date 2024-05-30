#!/bin/bash

# Ожидание постгреса
python3 /opt/app/core/wait_for_postgres.py

# Генерация миграции с автоматическим обнаружением изменений в модели
alembic -c /opt/app/alembic.ini revision --autogenerate -m "add migrations"

# Применение миграции к базе данных
alembic -c /opt/app/alembic.ini upgrade head

# Запуск вашего приложения
gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8005
