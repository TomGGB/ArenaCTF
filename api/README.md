# ArenaCTF API REST

API REST completa para la plataforma ArenaCTF, compatible con el formato de CTFd.

## 📚 Documentación

La API cuenta con documentación interactiva Swagger/OpenAPI disponible en:

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **Schema JSON**: `http://localhost:8000/api/schema/`

## 🔑 Autenticación

La API soporta dos métodos de autenticación:

### 1. Session Authentication (para uso desde el navegador)
Usa las sesiones de Django. Si estás autenticado en la web, automáticamente tendrás acceso a la API.

### 2. Token Authentication (para aplicaciones externas)
Usa tokens de API personalizados.

**Generar un token:**
```bash
# Desde la interfaz web: ir a /users/profile/ y generar token
# O desde la API:
POST /api/v1/tokens/
Authorization: Session (estar autenticado)
Body: {
    "description": "Mi token para app externa"
}
```

**Usar el token:**
```bash
curl -H "Authorization: Token TU_TOKEN_AQUI" http://localhost:8000/api/v1/challenges/
```

## 📍 Endpoints Principales

### Base URL: `/api/v1/`

### 👥 Users
- `GET /users/` - Listar usuarios
- `GET /users/{id}/` - Detalle de usuario
- `POST /users/` - Crear usuario (registro público)
- `GET /users/me/` - Usuario autenticado
- `GET /users/{id}/solves/` - Solves del usuario
- `GET /users/{id}/fails/` - Intentos fallidos (privado)

### 🏆 Teams
- `GET /teams/` - Listar equipos
- `GET /teams/{id}/` - Detalle de equipo
- `POST /teams/` - Crear equipo (requiere autenticación)
- `PATCH /teams/{id}/` - Actualizar equipo (solo miembros)
- `POST /teams/join/` - Unirse con código de invitación
- `POST /teams/{id}/leave/` - Abandonar equipo
- `GET /teams/{id}/solves/` - Solves del equipo
- `GET /teams/{id}/fails/` - Intentos fallidos (privado)
- `GET /teams/{id}/members/` - Miembros del equipo

### 🎯 Challenges
- `GET /challenges/` - Listar challenges activos
- `GET /challenges/{id}/` - Detalle de challenge
- `POST /challenges/` - Crear challenge (admin)
- `PATCH /challenges/{id}/` - Actualizar challenge (admin)
- `DELETE /challenges/{id}/` - Eliminar challenge (admin)
- `POST /challenges/attempt/` - Enviar flag
- `GET /challenges/{id}/solves/` - Ver quién resolvió
- `GET /challenges/{id}/files/` - Archivos del challenge

### 📂 Categories
- `GET /categories/` - Listar categorías
- `GET /categories/{id}/` - Detalle de categoría
- `POST /categories/` - Crear categoría (admin)
- `GET /categories/{id}/challenges/` - Challenges de la categoría

### 📝 Submissions
- `GET /submissions/` - Listar submissions (filtradas por permisos)
- `GET /submissions/{id}/` - Detalle de submission

### 🩸 First Bloods
- `GET /first-bloods/` - Listar first bloods
- `GET /first-bloods/{id}/` - Detalle de first blood

### 📊 Scoreboard
- `GET /scoreboard/` - Scoreboard completo
- `GET /scoreboard/top/` - Top N equipos (parámetro: `?count=10`)

### 📈 Statistics
- `GET /statistics/overview/` - Estadísticas generales
- `GET /statistics/challenges/` - Estadísticas de challenges

### ⚙️ Config
- `GET /config/` - Configuración del CTF
- `GET /config/current/` - Configuración actual
- `PATCH /config/{id}/` - Actualizar configuración (admin)

### 🏅 Achievements
- `GET /achievements/` - Listar logros
- `GET /achievements/{id}/` - Detalle de logro

## 💡 Ejemplos de Uso

### Obtener challenges activos
```bash
curl http://localhost:8000/api/v1/challenges/
```

### Enviar una flag (requiere autenticación)
```bash
curl -X POST http://localhost:8000/api/v1/challenges/attempt/ \
  -H "Authorization: Token TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": "uuid-del-challenge",
    "flag": "flag{example}"
  }'
```

### Crear un equipo
```bash
curl -X POST http://localhost:8000/api/v1/teams/ \
  -H "Authorization: Token TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Equipo",
    "color": "#FF5733"
  }'
```

### Unirse a un equipo
```bash
curl -X POST http://localhost:8000/api/v1/teams/join/ \
  -H "Authorization: Token TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "invite_code": "ABC12345"
  }'
```

### Ver scoreboard
```bash
curl http://localhost:8000/api/v1/scoreboard/
```

### Ver top 10
```bash
curl http://localhost:8000/api/v1/scoreboard/top/?count=10
```

## 🔍 Filtros y Búsqueda

La API soporta filtros, búsqueda y ordenamiento en la mayoría de endpoints:

```bash
# Filtrar challenges por categoría
GET /challenges/?category=uuid-de-categoria

# Buscar challenges por título
GET /challenges/?search=crypto

# Ordenar equipos por score
GET /teams/?ordering=-total_score

# Combinar múltiples filtros
GET /submissions/?team=uuid&is_correct=true&ordering=-submitted_at
```

## 🔐 Permisos

La API implementa varios niveles de permisos:

- **Público**: Challenges, equipos, scoreboard, estadísticas
- **Autenticado**: Crear equipos, enviar flags, ver propios submissions
- **Miembros del equipo**: Editar equipo, ver fails del equipo
- **Admin**: Crear/editar/eliminar challenges, ver todo

## 📄 Paginación

Los endpoints que retornan listas están paginados:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/challenges/?page=2",
  "previous": null,
  "results": [...]
}
```

Parámetros:
- `page`: Número de página
- `page_size`: Elementos por página (máx: 100)

## 🚀 Respuestas

Todas las respuestas son JSON con el siguiente formato:

**Éxito:**
```json
{
  "id": "uuid",
  "field1": "value",
  "field2": "value"
}
```

**Error:**
```json
{
  "error": "Mensaje de error"
}
```

## 🛠️ Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Ejecutar migraciones:
```bash
python manage.py makemigrations api
python manage.py migrate
```

3. Crear superusuario (opcional):
```bash
python manage.py createsuperuser
```

4. Iniciar servidor:
```bash
python manage.py runserver
```

5. Acceder a la documentación:
```
http://localhost:8000/api/docs/
```

## 🔧 Configuración Adicional

### CORS (para desarrollo)
En `settings.py`, CORS está habilitado en modo DEBUG. Para producción, configurar:

```python
CORS_ALLOWED_ORIGINS = [
    "https://tu-frontend.com",
]
```

### Rate Limiting
Para implementar rate limiting, puedes usar `django-ratelimit` o configurarlo en el proxy reverso (nginx).

## 📦 Compatibilidad con CTFd

Esta API está diseñada para ser compatible con el formato de CTFd, lo que permite:

- Usar herramientas existentes del ecosistema CTFd
- Migrar datos desde/hacia CTFd
- Integrar con clientes CTFd existentes

## 🤝 Contribuir

Para agregar nuevos endpoints o modificar la API:

1. Editar serializers en `api/serializers.py`
2. Editar viewsets en `api/views.py`
3. Agregar rutas en `api/urls.py`
4. Actualizar esta documentación

## 📞 Soporte

Si encuentras algún problema o tienes sugerencias:
- Crear issue en el repositorio
- Revisar la documentación Swagger
- Revisar los logs del servidor

## 📝 Notas

- Todos los UUIDs deben enviarse como strings
- Las fechas están en formato ISO 8601
- Los archivos se suben usando multipart/form-data
- La API respeta el estado del CTF (activo/inactivo)
