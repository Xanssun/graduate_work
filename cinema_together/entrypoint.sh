#!/bin/bash

# Ожижание постгреса
python3 /opt/app/core/wait_for_postgres.py

# Генерация миграции с автоматическим обнаружением изменений в модели
alembic -c /opt/app/alembic.ini revision --autogenerate -m "add migrations"

# Применение миграции к базе данных
alembic -c /opt/app/alembic.ini upgrade head

# Запуск вашего приложения
python3 /opt/app/main.py