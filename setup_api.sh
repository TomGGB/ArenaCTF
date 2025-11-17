#!/bin/bash
# Script para configurar la API en el contenedor Docker

echo "🚀 Configurando API de ArenaCTF..."

# Crear migraciones para la app api
echo "📝 Creando migraciones..."
python manage.py makemigrations api

# Aplicar migraciones
echo "💾 Aplicando migraciones..."
python manage.py migrate

# Crear superusuario si no existe (opcional)
echo "👤 Verificando superusuario..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print("No hay superusuario. Créalo con: python manage.py createsuperuser")
else:
    print("✅ Superusuario existe")
EOF

echo "✅ ¡Configuración completada!"
echo ""
echo "📚 Documentación disponible en:"
echo "   - Swagger UI: http://localhost:8000/api/docs/"
echo "   - ReDoc: http://localhost:8000/api/redoc/"
echo "   - Schema: http://localhost:8000/api/schema/"
echo ""
echo "🔑 Para generar un token de API:"
echo "   1. Inicia sesión en la web"
echo "   2. Ve a tu perfil de usuario"
echo "   3. O usa: POST /api/v1/tokens/"
