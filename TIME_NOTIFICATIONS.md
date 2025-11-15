# Sistema de Notificaciones de Tiempo del CTF

## Características Implementadas

### 1. Restricción de Tiempo
- Los participantes NO pueden enviar flags después de que el CTF finaliza
- Verificación tanto en backend (vista) como frontend (JavaScript)
- Mensaje de error claro cuando se intenta enviar después del tiempo

### 2. Notificaciones en Tiempo Real
El sistema envía alertas automáticas a todos los participantes conectados en estos momentos:
- **60 minutos** antes del fin
- **30 minutos** antes del fin
- **15 minutos** antes del fin
- **10 minutos** antes del fin
- **5 minutos** antes del fin
- **1 minuto** antes del fin

### 3. Notificación de Finalización
Cuando el CTF termina, todos los participantes reciben una notificación y la página se recarga automáticamente.

## Configuración

### Opción 1: Usando Docker Compose (Recomendado)

Actualiza tu `docker-compose.yml` para incluir el monitor de tiempo:

```yaml
services:
  web:
    # ... tu configuración existente ...
  
  time_monitor:
    build: .
    command: bash -c "while true; do python manage.py check_ctf_time; sleep 60; done"
    volumes:
      - .:/app
    depends_on:
      - web
      - redis
    environment:
      - DJANGO_SETTINGS_MODULE=ctf_platform.settings
```

Luego ejecuta:
```bash
docker-compose up -d
```

### Opción 2: Manualmente en Servidor

En una terminal separada, ejecuta:
```bash
chmod +x start_time_monitor.sh
./start_time_monitor.sh
```

O configura un cron job:
```bash
# Editar crontab
crontab -e

# Agregar esta línea (ejecutar cada minuto)
* * * * * cd /path/to/LanaCTF && python manage.py check_ctf_time
```

### Opción 3: Usando systemd (Linux)

Crea `/etc/systemd/system/ctf-time-monitor.service`:
```ini
[Unit]
Description=CTF Time Monitor
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/LanaCTF
ExecStart=/usr/bin/python3 /path/to/LanaCTF/manage.py check_ctf_time
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Luego:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ctf-time-monitor
sudo systemctl start ctf-time-monitor
```

## Configurar Fechas del CTF

Ve al panel de administración:
1. Ir a `/admin-panel/config/`
2. Configurar "Inicio del CTF" y "Fin del CTF"
3. Guardar cambios

## Cómo Funciona

1. **Monitor de Tiempo**: Se ejecuta cada minuto verificando el tiempo restante
2. **WebSocket**: Envía notificaciones en tiempo real a todos los usuarios conectados
3. **Verificación Backend**: La vista `submit_flag` rechaza submissions después del tiempo
4. **Verificación Frontend**: El JavaScript previene el envío de formularios
5. **Alertas Visuales**: La página de challenges muestra una alerta cuando el CTF termina

## Tipos de Alertas

- **Azul (60-16 minutos)**: Información general
- **Amarillo (15-6 minutos)**: Advertencia
- **Rojo (5-0 minutos)**: Crítico
- **Rojo + Borde (Finalizado)**: CTF terminado

## Notas Importantes

- Las notificaciones solo se muestran a usuarios con WebSocket conectado
- El monitor debe estar ejecutándose continuamente
- Las verificaciones son en tiempo del servidor (timezone configurado)
- Los administradores pueden seguir viendo challenges pero no enviar flags (a menos que se agregue excepción)
