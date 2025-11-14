# 🎮 CTF ARENA - Plataforma CTF Estilo Videojuego

Una plataforma de Capture The Flag (CTF) moderna con estética de videojuego, animaciones en tiempo real y actualizaciones instantáneas mediante WebSockets.

## ✨ Características

- 🎨 **Interfaz estilo videojuego** con animaciones dinámicas
- ⚡ **Actualizaciones en tiempo real** usando Django Channels y WebSockets
- 🩸 **Animaciones especiales** para First Bloods y flags capturadas
- 🏆 **Scoreboard dinámico** con rankings en vivo
- 🐳 **Completamente dockerizado** para fácil despliegue
- 📊 **Panel de administración** completo para gestionar el CTF
- 🎯 **Sistema de puntos dinámico** con bonus por First Blood
- 🔥 **Efectos visuales** tipo arcade con partículas y animaciones

## 🚀 Instalación Rápida

### Prerequisitos

- Docker y Docker Compose instalados
- Git

### Pasos

1. **Clonar el repositorio**
```bash
git clone <tu-repo>
cd LanaCTF
```

2. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Construir y levantar los contenedores**
```bash
docker-compose up --build
```

4. **Acceder a la plataforma**
- Frontend: http://localhost
- Admin: http://localhost/admin
  - Usuario: `admin`
  - Contraseña: `admin123`

## 🏗️ Arquitectura

```
LanaCTF/
├── ctf_platform/          # Configuración principal de Django
├── teams/                 # App de equipos
├── challenges/            # App de desafíos
├── scoreboard/            # App de scoreboard en tiempo real
├── templates/             # Templates HTML con animaciones
├── static/                # Archivos estáticos
├── docker-compose.yml     # Configuración de Docker
├── Dockerfile            # Imagen de Django
└── nginx.conf            # Configuración de Nginx
```

## 🎮 Características Técnicas

### Backend
- **Django 4.2** - Framework web
- **Django Channels** - WebSockets para tiempo real
- **PostgreSQL** - Base de datos
- **Redis** - Cache y channel layer
- **Daphne** - Servidor ASGI

### Frontend
- **CSS Animations** - Animaciones suaves y dinámicas
- **WebSockets** - Comunicación bidireccional
- **Canvas API** - Efectos de matriz y partículas
- **Font Awesome** - Iconos

### Infraestructura
- **Docker & Docker Compose** - Containerización
- **Nginx** - Reverse proxy y servidor de archivos estáticos

## 📱 Uso

### Para Administradores

1. Accede al panel de admin: `/admin`
2. Crea categorías de challenges (Web, Crypto, Forensics, etc.)
3. Agrega challenges con sus flags
4. Los equipos se registran y empiezan a competir

### Para Participantes

1. Registra tu equipo
2. Navega por los challenges
3. Envía flags para ganar puntos
4. ¡Compite por el primer lugar en el scoreboard!

## 🎨 Animaciones Especiales

### First Blood 🩸
Cuando un equipo es el primero en resolver un challenge:
- Animación de pulso rojo
- Notificación especial en pantalla
- Efecto de brillo y partículas
- Sonido especial (configurable)

### Flag Capturada 🚩
Cuando se resuelve un challenge:
- Animación de entrada lateral
- Actualización automática del scoreboard
- Efectos de partículas
- Actualización de puntos en tiempo real

### Scoreboard Dinámico 🏆
- Actualización automática cada 30 segundos
- Animaciones de cambio de posición
- Colores personalizados por equipo
- Efectos especiales para top 3

## 🔧 Configuración Avanzada

### Variables de Entorno

```env
DEBUG=True                    # Modo debug
SECRET_KEY=tu-clave-secreta  # Clave secreta de Django
DATABASE_NAME=ctf_db         # Nombre de la BD
DATABASE_USER=ctf_user       # Usuario de la BD
DATABASE_PASSWORD=password   # Contraseña de la BD
DATABASE_HOST=db             # Host de la BD
REDIS_HOST=redis             # Host de Redis
```

### Personalizar Colores

Edita las variables CSS en `templates/base.html`:

```css
:root {
    --primary-color: #00ff41;    /* Verde neón */
    --secondary-color: #ff00ff;  /* Magenta */
    --danger-color: #ff0000;     /* Rojo */
    --background: #0a0e27;       /* Fondo oscuro */
}
```

## 📊 Monitoreo

### Ver logs
```bash
docker-compose logs -f web
```

### Acceder a la base de datos
```bash
docker-compose exec db psql -U ctf_user -d ctf_db
```

### Acceder al contenedor de Django
```bash
docker-compose exec web bash
```

## 🛠️ Comandos Útiles

```bash
# Crear migraciones
docker-compose exec web python manage.py makemigrations

# Aplicar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Recolectar archivos estáticos
docker-compose exec web python manage.py collectstatic

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v
```

## 🎯 Roadmap

- [ ] Sistema de hints con penalización
- [ ] Gráficas de progreso por equipo
- [ ] Chat en tiempo real
- [ ] Sistema de logros y badges
- [ ] API REST completa
- [ ] Modo torneo con rounds
- [ ] Integración con Discord
- [ ] Sistema de replays

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 👥 Créditos

Desarrollado con ❤️ para la comunidad CTF

---

**¡Disfruta tu CTF y que gane el mejor equipo! 🎮🏆**
