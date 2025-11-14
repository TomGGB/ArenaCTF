#!/bin/bash

# Script de inicio rápido para la plataforma CTF

echo "🎮 CTF ARENA - Inicio Rápido"
echo "============================"
echo ""

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

# Copiar archivo de variables de entorno si no existe
if [ ! -f .env ]; then
    echo "📋 Copiando archivo de configuración..."
    cp .env.example .env
    echo "✓ Archivo .env creado"
fi

echo ""
echo "🏗️  Construyendo contenedores..."
docker-compose build

echo ""
echo "🚀 Iniciando servicios..."
docker-compose up -d

echo ""
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

echo ""
echo "📊 Inicializando datos de ejemplo..."
docker-compose exec -T web python manage.py init_data

echo ""
echo "✅ ¡Plataforma iniciada exitosamente!"
echo ""
echo "📍 Accede a la plataforma en:"
echo "   🌐 Frontend: http://localhost"
echo "   ⚙️  Admin: http://localhost/admin"
echo ""
echo "🔑 Credenciales de administrador:"
echo "   Usuario: admin"
echo "   Contraseña: admin123"
echo ""
echo "📝 Comandos útiles:"
echo "   Ver logs: docker-compose logs -f"
echo "   Detener: docker-compose down"
echo "   Reiniciar: docker-compose restart"
echo ""
echo "🎉 ¡Disfruta tu CTF!"
