#!/bin/bash

set -e

echo "Esperando a Redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "Redis iniciado"

echo "Aplicando migraciones..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando servidor..."
exec daphne -b 0.0.0.0 -p 8000 ctf_platform.asgi:application
