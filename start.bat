@echo off
REM Script de inicio rápido para Windows

echo 🎮 CTF ARENA - Inicio Rápido
echo ============================
echo.

REM Verificar si Docker está instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no está instalado. Por favor instala Docker primero.
    pause
    exit /b 1
)

REM Verificar si Docker Compose está instalado
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose no está instalado. Por favor instala Docker Compose primero.
    pause
    exit /b 1
)

REM Copiar archivo de variables de entorno si no existe
if not exist .env (
    echo 📋 Copiando archivo de configuración...
    copy .env.example .env
    echo ✓ Archivo .env creado
)

echo.
echo 🏗️  Construyendo contenedores...
docker-compose build

echo.
echo 🚀 Iniciando servicios...
docker-compose up -d

echo.
echo ⏳ Esperando a que los servicios estén listos...
timeout /t 10 /nobreak >nul

echo.
echo 📊 Inicializando datos de ejemplo...
docker-compose exec -T web python manage.py init_data

echo.
echo ✅ ¡Plataforma iniciada exitosamente!
echo.
echo 📍 Accede a la plataforma en:
echo    🌐 Frontend: http://localhost
echo    ⚙️  Admin: http://localhost/admin
echo.
echo 🔑 Credenciales de administrador:
echo    Usuario: admin
echo    Contraseña: admin123
echo.
echo 📝 Comandos útiles:
echo    Ver logs: docker-compose logs -f
echo    Detener: docker-compose down
echo    Reiniciar: docker-compose restart
echo.
echo 🎉 ¡Disfruta tu CTF!
echo.
pause
