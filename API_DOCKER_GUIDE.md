# 🐳 API REST en Docker - Guía de Uso

## 🚀 Configuración Inicial

### 1. Aplicar las migraciones dentro del contenedor

```bash
# Ejecutar el script de configuración
docker-compose exec web bash setup_api.sh

# O manualmente:
docker-compose exec web python manage.py makemigrations api
docker-compose exec web python manage.py migrate
```

### 2. Crear un superusuario (si no existe)

```bash
docker-compose exec web python manage.py createsuperuser
```

### 3. Reiniciar el contenedor

```bash
docker-compose restart web
```

## 📚 Acceder a la Documentación

Una vez que el contenedor esté corriendo, la documentación está disponible en:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema JSON**: http://localhost:8000/api/schema/

## 🔑 Generar Token de API

### Opción 1: Desde la interfaz web
1. Inicia sesión en http://localhost:8000
2. Ve a tu perfil de usuario
3. Genera un nuevo token

### Opción 2: Desde el shell de Django
```bash
docker-compose exec web python manage.py shell
```

Luego ejecuta:
```python
from django.contrib.auth import get_user_model
from api.models import APIToken

User = get_user_model()
user = User.objects.get(username='tu_usuario')
token = APIToken.objects.create(user=user, description='Mi token de prueba')
print(f"Token: {token.key}")
```

### Opción 3: Desde la API (requiere estar autenticado)
```bash
curl -X POST http://localhost:8000/api/v1/tokens/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"description": "Token desde curl"}'
```

## 💡 Ejemplos de Uso con Docker

### Ver challenges disponibles
```bash
curl http://localhost:8000/api/v1/challenges/
```

### Enviar una flag (con token)
```bash
curl -X POST http://localhost:8000/api/v1/challenges/attempt/ \
  -H "Authorization: Token TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": "uuid-del-challenge",
    "flag": "flag{example}"
  }'
```

### Ver el scoreboard
```bash
curl http://localhost:8000/api/v1/scoreboard/
```

### Crear un equipo (con token)
```bash
curl -X POST http://localhost:8000/api/v1/teams/ \
  -H "Authorization: Token TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Equipo",
    "color": "#FF5733"
  }'
```

### Ver estadísticas
```bash
curl http://localhost:8000/api/v1/statistics/overview/
```

## 🔍 Debugging en Docker

### Ver logs del contenedor
```bash
docker-compose logs -f web
```

### Acceder al shell del contenedor
```bash
docker-compose exec web bash
```

### Verificar que la API funciona
```bash
# Dentro del contenedor
curl http://localhost:8000/api/v1/challenges/

# Desde tu máquina host
curl http://localhost:8000/api/v1/challenges/
```

### Verificar migraciones
```bash
docker-compose exec web python manage.py showmigrations api
```

## 🛠️ Comandos Útiles

### Reconstruir el contenedor con los cambios
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Ver todos los endpoints disponibles
```bash
docker-compose exec web python manage.py show_urls
```

### Testear la API desde dentro del contenedor
```bash
docker-compose exec web python manage.py shell
```
```python
from rest_framework.test import APIClient
client = APIClient()
response = client.get('/api/v1/challenges/')
print(response.status_code)
print(response.json())
```

## 🔐 Configuración de CORS (si usas frontend separado)

Si tienes un frontend en otro puerto/dominio, edita `ctf_platform/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React, Vue, etc.
    "http://localhost:5173",  # Vite
]
```

Luego reconstruye:
```bash
docker-compose restart web
```

## 📊 Monitoreo

### Ver requests en tiempo real
```bash
docker-compose logs -f web | grep "GET\|POST\|PUT\|PATCH\|DELETE"
```

### Ver solo errores
```bash
docker-compose logs -f web | grep "ERROR\|Exception"
```

## 🎯 Endpoints Principales

Todos disponibles en `/api/v1/`:

- `/users/` - Usuarios
- `/teams/` - Equipos
- `/challenges/` - Challenges
- `/challenges/attempt/` - Enviar flags
- `/categories/` - Categorías
- `/submissions/` - Submissions
- `/first-bloods/` - First bloods
- `/scoreboard/` - Scoreboard
- `/statistics/overview/` - Estadísticas
- `/config/` - Configuración del CTF
- `/achievements/` - Logros
- `/tokens/` - Gestión de tokens

## 🚨 Troubleshooting

### Error: "Module not found"
```bash
docker-compose exec web pip install -r requirements.txt
docker-compose restart web
```

### Error: "no such table: api_apitoken"
```bash
docker-compose exec web python manage.py migrate api
```

### La documentación Swagger no carga
1. Verifica que `drf-spectacular` esté instalado
2. Verifica que la app `api` esté en `INSTALLED_APPS`
3. Revisa los logs: `docker-compose logs web`

### Error 403 Forbidden
- Verifica que el token sea correcto
- Verifica que el CTF esté activo
- Verifica que el usuario tenga un equipo (para enviar flags)

## 📦 Persistencia de Datos

Los tokens de API se guardan en la base de datos SQLite que está en el volumen del contenedor. Para hacer backup:

```bash
docker-compose exec web python manage.py dumpdata api.APIToken > api_tokens_backup.json
```

Para restaurar:
```bash
docker cp api_tokens_backup.json arenactf_web_1:/app/
docker-compose exec web python manage.py loaddata api_tokens_backup.json
```

## 🔄 Actualizar la API

Después de hacer cambios en el código:

```bash
# Si cambiaste modelos
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Reiniciar
docker-compose restart web
```

## 📝 Ejemplo Completo de Flujo

```bash
# 1. Levantar los contenedores
docker-compose up -d

# 2. Configurar la API
docker-compose exec web bash setup_api.sh

# 3. Crear usuario
docker-compose exec web python manage.py createsuperuser

# 4. Generar token (desde el shell)
docker-compose exec web python manage.py shell
# >>> from api.models import APIToken
# >>> from django.contrib.auth import get_user_model
# >>> User = get_user_model()
# >>> user = User.objects.first()
# >>> token = APIToken.objects.create(user=user, description='Test')
# >>> print(token.key)

# 5. Probar la API
curl http://localhost:8000/api/v1/challenges/

# 6. Ver documentación
# Abrir en el navegador: http://localhost:8000/api/docs/
```

## 🎉 ¡Listo!

Tu API REST está funcionando en Docker. Ahora puedes:

✅ Integrar con aplicaciones externas
✅ Automatizar challenges
✅ Crear dashboards personalizados
✅ Usar herramientas CTF existentes
✅ Construir bots de Discord/Telegram
✅ Análisis de datos en tiempo real
