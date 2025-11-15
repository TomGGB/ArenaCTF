#!/bin/bash
# Script para iniciar el monitor de tiempo del CTF

echo "Iniciando monitor de tiempo del CTF..."

# Ejecutar el comando cada minuto
while true; do
    python manage.py check_ctf_time
    sleep 60
done
