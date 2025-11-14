# 🎮 Guía de Uso - CTF ARENA

## 📚 Índice

1. [Inicio Rápido](#inicio-rápido)
2. [Administración](#administración)
3. [Para Participantes](#para-participantes)
4. [Personalización](#personalización)
5. [Troubleshooting](#troubleshooting)

## 🚀 Inicio Rápido

### Windows

```cmd
start.bat
```

### Linux/Mac

```bash
chmod +x start.sh
./start.sh
```

### Manual

```bash
# 1. Copiar variables de entorno
cp .env.example .env

# 2. Construir e iniciar
docker-compose up --build -d

# 3. Inicializar datos de ejemplo
docker-compose exec web python manage.py init_data
```

## 👨‍💼 Administración

### Acceso al Panel de Admin

1. Ve a: `http://localhost/admin`
2. Usuario: `admin`
3. Contraseña: `admin123`

**⚠️ IMPORTANTE: Cambia la contraseña por defecto en producción**

### Crear Categorías

1. Ve a **Categorías** en el panel admin
2. Click en "Agregar Categoría"
3. Completa:
   - **Nombre**: Web, Crypto, Forensics, etc.
   - **Icono**: Emoji o símbolo (🌐, 🔐, 🔍)
   - **Color**: Color en formato hex (#00ff41)

### Crear Challenges

1. Ve a **Challenges** en el panel admin
2. Click en "Agregar Challenge"
3. Completa:
   - **Título**: Nombre del challenge
   - **Descripción**: Explicación detallada
   - **Categoría**: Selecciona la categoría
   - **Puntos**: Valor en puntos
   - **Flag**: La flag correcta (ej: flag{example})
   - **Archivos**: (Opcional) Archivos necesarios
   - **Pistas**: (Opcional) Pistas para ayudar
   - **Activo**: Marcar para que sea visible

### Gestionar Equipos

- Los equipos se registran desde el frontend
- En el panel admin puedes:
  - Ver todos los equipos
  - Editar miembros
  - Modificar puntuaciones (si es necesario)
  - Ver estadísticas

### Ver Submissions

Monitorea todos los intentos de flags:
- Correctas e incorrectas
- Por equipo
- Por challenge
- Timestamp de cada intento

## 👥 Para Participantes

### 1. Registrar Equipo

1. Ve a: `http://localhost/teams/register/`
2. Ingresa:
   - Nombre del equipo
   - Color del equipo (para identificación en scoreboard)
3. Click en "Crear Equipo"

### 2. Ver Challenges

1. Ve a: `http://localhost/challenges/`
2. Explora las categorías
3. Click en un challenge para ver detalles

### 3. Enviar Flags

1. Abre un challenge
2. Lee la descripción y pistas
3. Ingresa la flag en el formato correcto
4. Click en "Enviar Flag"

### 4. Monitorear Scoreboard

- Ve a: `http://localhost/`
- Observa el scoreboard en tiempo real
- Ve las animaciones cuando se resuelven challenges
- Celebra los First Bloods! 🩸

## 🎨 Personalización

### Cambiar Colores del Tema

Edita `templates/base.html`:

```css
:root {
    --primary-color: #00ff41;    /* Verde neón */
    --secondary-color: #ff00ff;  /* Magenta */
    --danger-color: #ff0000;     /* Rojo */
    --background: #0a0e27;       /* Fondo oscuro */
    --surface: #1a1f3a;         /* Superficie */
}
```

### Personalizar Animaciones

Puedes modificar las animaciones en:
- `templates/base.html` - Animaciones globales
- `templates/scoreboard/dashboard.html` - Animaciones del scoreboard
- `templates/challenges/list.html` - Animaciones de challenges

### Agregar Sonidos

En `templates/base.html`, actualiza la función `playSound()`:

```javascript
function playSound(type) {
    const audio = new Audio();
    if (type === 'firstblood') {
        audio.src = '/static/sounds/firstblood.mp3';
    } else if (type === 'flag') {
        audio.src = '/static/sounds/flag.mp3';
    }
    audio.play();
}
```

### Cambiar Logo/Título

Edita en `templates/base.html`:

```html
<h1>🎮 TU NOMBRE CTF 🎮</h1>
```

## 🔧 Troubleshooting

### Los contenedores no inician

```bash
# Ver logs
docker-compose logs

# Reintentar
docker-compose down
docker-compose up --build
```

### Error de conexión a la base de datos

```bash
# Esperar más tiempo para que PostgreSQL inicie
docker-compose logs db

# Verificar que el contenedor esté corriendo
docker-compose ps
```

### WebSocket no conecta

1. Verifica que Redis esté corriendo:
```bash
docker-compose ps redis
```

2. Revisa los logs de web:
```bash
docker-compose logs web
```

3. En el navegador, abre la consola de desarrollador y busca errores de WebSocket

### Las migraciones no se aplican

```bash
# Aplicar manualmente
docker-compose exec web python manage.py migrate

# Si hay errores, reiniciar la base de datos
docker-compose down -v
docker-compose up --build
```

### Los archivos estáticos no cargan

```bash
# Recolectar archivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Reiniciar nginx
docker-compose restart nginx
```

### Cambiar contraseña de admin

```bash
docker-compose exec web python manage.py changepassword admin
```

### Resetear toda la plataforma

```bash
# ⚠️ ESTO BORRARÁ TODOS LOS DATOS
docker-compose down -v
docker-compose up --build
```

## 📊 Comandos Útiles

### Ver logs en tiempo real
```bash
docker-compose logs -f
```

### Acceder al shell de Django
```bash
docker-compose exec web python manage.py shell
```

### Acceder a la base de datos
```bash
docker-compose exec db psql -U ctf_user -d ctf_db
```

### Crear backup de la base de datos
```bash
docker-compose exec db pg_dump -U ctf_user ctf_db > backup.sql
```

### Restaurar backup
```bash
cat backup.sql | docker-compose exec -T db psql -U ctf_user -d ctf_db
```

### Ver uso de recursos
```bash
docker stats
```

## 🎯 Tips para Organizar un CTF

1. **Antes del evento:**
   - Prueba todos los challenges
   - Verifica que las flags sean correctas
   - Configura el scoreboard en una pantalla grande
   - Prepara un canal de Discord/Telegram para soporte

2. **Durante el evento:**
   - Monitorea el panel de admin regularmente
   - Observa las submissions para detectar problemas
   - Mantén comunicación con los participantes
   - Celebra los First Bloods con animaciones

3. **Después del evento:**
   - Exporta el scoreboard final
   - Crea un backup de la base de datos
   - Recolecta feedback de los participantes
   - Documenta los writeups

## 🆘 Soporte

Si encuentras problemas:

1. Revisa esta guía
2. Consulta los logs: `docker-compose logs`
3. Busca en GitHub Issues
4. Crea un nuevo issue con:
   - Descripción del problema
   - Logs relevantes
   - Pasos para reproducir

---

**¡Que tengas un excelente CTF! 🎮🏆**
