# ✅ API REST de ArenaCTF - Instalación Completada

## 🎉 ¡La API está funcionando!

Tu plataforma ArenaCTF ahora cuenta con una API REST completa compatible con CTFd.

## 📍 URLs Disponibles

### Documentación Interactiva
- **Swagger UI**: http://localhost/api/docs/
- **ReDoc**: http://localhost/api/redoc/
- **Schema OpenAPI**: http://localhost/api/schema/

### Base de la API
- **API v1**: http://localhost/api/v1/

## 🔥 Prueba Rápida

```bash
# Ver todos los challenges
curl http://localhost/api/v1/challenges/

# Ver el scoreboard
curl http://localhost/api/v1/scoreboard/

# Ver estadísticas
curl http://localhost/api/v1/statistics/overview/

# Ver equipos
curl http://localhost/api/v1/teams/

# Ver categorías
curl http://localhost/api/v1/categories/

# Ver first bloods
curl http://localhost/api/v1/first-bloods/
```

## 📚 Endpoints Principales

### Challenges
- `GET /api/v1/challenges/` - Listar challenges
- `GET /api/v1/challenges/{id}/` - Detalle de challenge
- `POST /api/v1/challenges/attempt/` - Enviar flag ⚠️ Requiere auth + equipo
- `GET /api/v1/challenges/{id}/solves/` - Ver quién resolvió
- `GET /api/v1/challenges/{id}/files/` - Archivos del challenge

### Teams
- `GET /api/v1/teams/` - Listar equipos
- `GET /api/v1/teams/{id}/` - Detalle de equipo
- `POST /api/v1/teams/` - Crear equipo ⚠️ Requiere auth
- `POST /api/v1/teams/join/` - Unirse con código
- `GET /api/v1/teams/{id}/solves/` - Solves del equipo

### Users
- `GET /api/v1/users/` - Listar usuarios
- `GET /api/v1/users/me/` - Usuario autenticado ⚠️ Requiere auth
- `POST /api/v1/users/` - Registrar usuario (público)
- `GET /api/v1/users/{id}/solves/` - Solves del usuario

### Scoreboard
- `GET /api/v1/scoreboard/` - Scoreboard completo
- `GET /api/v1/scoreboard/top/?count=10` - Top N equipos

### Statistics
- `GET /api/v1/statistics/overview/` - Estadísticas generales
- `GET /api/v1/statistics/challenges/` - Stats de challenges

### Other
- `GET /api/v1/categories/` - Categorías
- `GET /api/v1/submissions/` - Submissions (privado)
- `GET /api/v1/first-bloods/` - First bloods
- `GET /api/v1/config/current/` - Configuración del CTF
- `GET /api/v1/achievements/` - Logros

## 🔑 Autenticación

### Para usuarios web (Session Auth)
Si estás autenticado en la web, automáticamente puedes usar la API desde el navegador.

### Para aplicaciones externas (Token Auth)

1. **Generar un token desde el shell de Django:**

```bash
docker-compose exec web python manage.py shell
```

Luego ejecuta:
```python
from django.contrib.auth import get_user_model
from api.models import APIToken

User = get_user_model()
user = User.objects.get(username='admin')  # Cambia 'admin' por tu usuario
token = APIToken.objects.create(user=user, description='Mi token')
print(f"Token: {token.key}")
```

2. **Usar el token:**

```bash
curl -H "Authorization: Token TU_TOKEN_AQUI" http://localhost/api/v1/challenges/attempt/
```

## 💡 Ejemplo Completo: Resolver un Challenge

```bash
# 1. Obtener un token (desde el shell como arriba)

# 2. Ver challenges disponibles
curl http://localhost/api/v1/challenges/

# 3. Copiar el ID del challenge que quieres resolver

# 4. Enviar la flag
curl -X POST http://localhost/api/v1/challenges/attempt/ \
  -H "Authorization: Token TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": "8b88599f-e665-4c0c-8799-c2bbe927d1d6",
    "flag": "flag{tu_respuesta}"
  }'

# Respuesta si es correcta:
# {
#   "success": true,
#   "is_correct": true,
#   "message": "¡Correcto! Has ganado 100 puntos",
#   "points_earned": 100,
#   "team_score": 100,
#   "first_blood": false,
#   "submission_id": "uuid"
# }
```

## 🛠️ Casos de Uso

### 1. Bot de Discord
```python
import discord
import requests

API_URL = "http://localhost/api/v1"
TOKEN = "tu_token_aqui"

@bot.command()
async def scoreboard(ctx):
    response = requests.get(f"{API_URL}/scoreboard/")
    data = response.json()
    # Formatear y enviar el scoreboard
```

### 2. Dashboard Personalizado
```javascript
fetch('http://localhost/api/v1/scoreboard/')
  .then(res => res.json())
  .then(data => {
    // Renderizar scoreboard en React/Vue/etc
  });
```

### 3. Automatización de Challenges
```python
import requests

headers = {"Authorization": f"Token {TOKEN}"}

def submit_flag(challenge_id, flag):
    response = requests.post(
        "http://localhost/api/v1/challenges/attempt/",
        headers=headers,
        json={"challenge_id": challenge_id, "flag": flag}
    )
    return response.json()
```

### 4. Exportar Datos
```bash
# Exportar todos los challenges
curl http://localhost/api/v1/challenges/ > challenges.json

# Exportar scoreboard
curl http://localhost/api/v1/scoreboard/ > scoreboard.json

# Exportar estadísticas
curl http://localhost/api/v1/statistics/overview/ > stats.json
```

## 📊 Filtros y Búsqueda

```bash
# Filtrar challenges por categoría
curl "http://localhost/api/v1/challenges/?category=uuid"

# Buscar challenges por texto
curl "http://localhost/api/v1/challenges/?search=web"

# Ordenar equipos por score
curl "http://localhost/api/v1/teams/?ordering=-total_score"

# Paginación
curl "http://localhost/api/v1/challenges/?page=2&page_size=10"

# Combinar filtros
curl "http://localhost/api/v1/submissions/?team=uuid&is_correct=true"
```

## 🔐 Permisos

| Acción | Permiso Requerido |
|--------|-------------------|
| Ver challenges, equipos, scoreboard | Público |
| Enviar flags | Autenticado + Tener equipo |
| Crear equipo | Autenticado |
| Editar equipo | Miembro del equipo |
| Ver submissions propias | Autenticado |
| Crear/editar challenges | Admin |
| Ver todas las submissions | Admin |

## 🐛 Troubleshooting

### No puedo enviar flags
1. Verifica que estés autenticado (token válido)
2. Verifica que pertenezcas a un equipo
3. Verifica que el CTF esté activo
4. Verifica que no hayas resuelto ya ese challenge

### Error 404 en la API
- Verifica que la URL sea correcta: `http://localhost/api/v1/...`
- Nota: Es el puerto 80 (a través de nginx), no 8000

### Token no funciona
- Verifica que el header sea: `Authorization: Token TU_TOKEN`
- Nota: "Token" con T mayúscula y un espacio antes del token

### Ver logs en tiempo real
```bash
docker-compose logs -f web
```

## 📖 Documentación Completa

Para más detalles, consulta:
- `api/README.md` - Documentación completa de la API
- `API_DOCKER_GUIDE.md` - Guía específica para Docker
- http://localhost/api/docs/ - Documentación interactiva Swagger

## 🎯 Próximos Pasos

1. **Explora la documentación Swagger**: http://localhost/api/docs/
2. **Genera un token de API** para tus integraciones
3. **Prueba los endpoints** con curl o Postman
4. **Construye integraciones** personalizadas
5. **Crea dashboards** con tus frameworks favoritos

## 📞 Soporte

- Swagger UI tiene ejemplos interactivos para cada endpoint
- Todos los endpoints incluyen documentación detallada
- Los errores incluyen mensajes descriptivos en español

---

## ✨ Características Implementadas

✅ Autenticación con tokens de API
✅ Documentación Swagger/OpenAPI interactiva
✅ Filtros y búsqueda en todos los endpoints
✅ Paginación automática
✅ Permisos granulares
✅ Compatible con formato CTFd
✅ CORS configurado
✅ Respuestas en JSON
✅ Validación de datos
✅ Manejo de errores en español
✅ Endpoints públicos y privados
✅ Support para Session y Token authentication

## 🚀 ¡Disfruta tu API REST!

Tu plataforma CTF ahora es completamente programable y puede integrarse con cualquier herramienta o servicio externo.
