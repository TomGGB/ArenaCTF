# 🏆 ArenaCTF

**ArenaCTF** es una plataforma completa de Capture The Flag (CTF) construida con Django, diseñada para hospedar competencias de seguridad informática con características profesionales y en tiempo real.

![Django](https://img.shields.io/badge/Django-4.2-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Características Principales

### 🎯 Sistema de Challenges
- Categorías personalizables con iconos y colores
- Sistema de puntos dinámico
- Soporte para archivos adjuntos
- First Blood con bonificación de puntos configurable
- Validación de flags en tiempo real

### 👥 Gestión de Equipos
- Sistema de códigos de invitación únicos (8 caracteres)
- Códigos privados solo visibles para miembros
- Estadísticas detalladas por equipo
- Tracking de solves y first bloods
- Rankings en tiempo real

### 📊 Scoreboard Dinámico
- Actualización en tiempo real via WebSockets
- Gráfico de progreso temporal (Chart.js)
- Rankings con medallas (🥇🥈🥉)
- Historial de actividad reciente
- Display público para proyectores con animaciones y sonidos

### 🎪 Display Público Interactivo
- **Notificaciones en tiempo real** con cola ordenada
- **Efectos de sonido** generados dinámicamente para cada evento
- **Animaciones visuales** profesionales:
  - Fade-in para nuevos elementos
  - Slide-in para actividad reciente
  - Pulse-glow para cambios de puntuación
  - Rank-up/rank-down para cambios de posición
  - First Blood flash effect
- **Notificaciones overlay** centrales (4 segundos cada una)
- Sistema de eventos: flags resueltas, first bloods, cambios de ranking

### ⚙️ Panel de Administración Completo
- Dashboard con estadísticas en tiempo real
- CRUD completo de challenges, categorías, equipos y usuarios
- Sistema de baneos de usuarios
- Gestión de submissions
- Editor de configuración del CTF
- Filas clickeables en tablas para navegación rápida

### 👤 Sistema de Usuarios
- Autenticación segura con UUIDs
- Perfiles de usuario personalizables
- Cambio de contraseña
- Middleware de verificación de usuarios baneados
- Dropdown de navegación en navbar

### 🔧 Configuración Avanzada
- Nombre personalizable del CTF
- Fechas de inicio y fin configurables
- Puntos de First Blood ajustables
- Timezone configurable (10 zonas disponibles)
- Todo configurable desde el panel admin

### 🎨 Interfaz Moderna
- DaisyUI + Tailwind CSS
- Tema dark mode
- Fuente Rajdhani (gaming style)
- Navbar sticky
- Responsive design
- Animaciones suaves

## 🚀 Tecnologías

- **Backend:** Django 4.2, Python 3.11
- **Base de datos:** SQLite (fácilmente cambiable a PostgreSQL/MySQL)
- **WebSockets:** Django Channels + Redis
- **Frontend:** DaisyUI 4.4.19, Tailwind CSS, Chart.js 4.4.0
- **Containerización:** Docker + Docker Compose
- **Web Server:** Nginx + Daphne (ASGI)

## 📦 Instalación Rápida con Docker

### Prerrequisitos
- Docker
- Docker Compose

### Pasos

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tuusuario/ArenaCTF.git
cd ArenaCTF
```

2. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Levantar los contenedores:**
```bash
docker-compose up -d
```

4. **Aplicar migraciones:**
```bash
docker-compose exec web python manage.py migrate
```

5. **Acceder a la plataforma:**
- Plataforma principal: http://localhost
- Panel admin: http://localhost/admin-panel/
- Display público: http://localhost/display/

### Configuración Inicial (Quickstart)

Al acceder por primera vez, serás redirigido al quickstart donde podrás:
1. Crear el usuario administrador
2. Configurar el nombre y fechas del CTF
3. ¡Empezar a usar la plataforma!

## 🛠️ Instalación Manual (Desarrollo)

```bash
# Clonar repositorio
git clone https://github.com/tuusuario/ArenaCTF.git
cd ArenaCTF

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
python manage.py migrate

# Inicializar datos (opcional)
python manage.py init_data

# Levantar Redis (requerido para WebSockets)
docker run -d -p 6379:6379 redis:alpine

# Ejecutar servidor de desarrollo
python manage.py runserver
```

## 📁 Estructura del Proyecto

```
ArenaCTF/
├── admin_panel/         # Panel de administración personalizado
├── challenges/          # App de challenges y submissions
├── ctf_platform/        # Configuración principal del proyecto
├── media/               # Archivos subidos (avatares, archivos de challenges)
├── quickstart/          # Wizard de configuración inicial
├── scoreboard/          # Scoreboard y display público
├── static/              # Archivos estáticos (CSS, JS, sonidos)
├── staticfiles/         # Archivos estáticos recolectados
├── teams/               # Gestión de equipos
├── templates/           # Templates HTML
├── users/               # Sistema de usuarios personalizado
├── docker-compose.yml   # Configuración de Docker Compose
├── Dockerfile           # Imagen de Docker
├── nginx.conf           # Configuración de Nginx
├── requirements.txt     # Dependencias de Python
└── manage.py            # Utilidad de gestión de Django
```

## 🎮 Uso

### Para Participantes

1. **Registro:** Crear cuenta en `/register/`
2. **Crear o unirse a equipo:** 
   - Crear nuevo equipo en `/teams/register/`
   - O unirse con código en `/teams/join/`
3. **Ver challenges:** Acceder a `/challenges/`
4. **Resolver:** Enviar flags y ganar puntos
5. **Ver ranking:** Dashboard en `/`

### Para Administradores

1. **Acceder al panel:** `/admin-panel/`
2. **Configurar CTF:** Nombre, fechas, puntos de first blood
3. **Crear categorías:** Asignar colores e iconos
4. **Crear challenges:** Título, descripción, flag, puntos, archivos
5. **Gestionar usuarios/equipos:** Ver, editar, banear
6. **Monitorear submissions:** Ver todos los intentos
7. **Display público:** `/display/` para proyectar en pantalla grande

## 🔐 Seguridad

- UUIDs en lugar de IDs secuenciales
- Validación CSRF habilitada
- Sistema de baneos de usuarios
- Códigos de invitación de equipos privados
- Middleware de verificación de usuarios activos
- ALLOWED_HOSTS configurado

## 🎨 Personalización

### Cambiar Tema
Edita `templates/base.html` y cambia `data-theme="dark"` a cualquier tema de DaisyUI.

### Agregar Sonidos Personalizados
Coloca archivos de audio en `static/sounds/` y referéncialos en los templates.

### Modificar Puntos de First Blood
Panel Admin → Configuración CTF → Puntos de First Blood

### Agregar Zonas Horarias
Edita `templates/admin_panel/config.html` en el select de timezone.

## 📊 Comandos Útiles

```bash
# Recalcular scores de todos los equipos
python manage.py recalculate_scores

# Crear datos de prueba
python manage.py init_data

# Recolectar archivos estáticos
python manage.py collectstatic

# Crear superusuario (si no usaste quickstart)
python manage.py createsuperuser
```

## 🐳 Docker Compose

Servicios incluidos:
- **web:** Aplicación Django con Daphne (ASGI)
- **redis:** Cache y backend de channels
- **nginx:** Proxy reverso y servidor de archivos estáticos

Puertos:
- `80`: Nginx (HTTP)
- `8000`: Django (desarrollo directo)
- `6379`: Redis (interno)

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- Django Framework
- DaisyUI y Tailwind CSS
- Chart.js
- Django Channels
- Comunidad CTF

## 📞 Soporte

Para reportar bugs o sugerir features, abre un issue en GitHub.

---

**¡Hecho con ❤️ para la comunidad CTF!**
