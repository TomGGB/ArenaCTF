# 🏗️ Arquitectura de CTF ARENA

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Browser)                       │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │   Dashboard    │  │   Challenges   │  │     Teams      │   │
│  │  (WebSocket)   │  │  (REST API)    │  │   (Forms)      │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                    HTTP / WebSocket
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      NGINX (Port 80)                             │
│              Reverse Proxy & Static Files Server                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                    Proxy to Port 8000
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                   DJANGO + DAPHNE (Port 8000)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Django Channels (ASGI)                       │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │  │
│  │  │ Scoreboard │  │ Challenges │  │   Teams    │        │  │
│  │  │    App     │  │    App     │  │    App     │        │  │
│  │  └────────────┘  └────────────┘  └────────────┘        │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────┐        │  │
│  │  │        WebSocket Consumers                 │        │  │
│  │  │   (Real-time Scoreboard Updates)          │        │  │
│  │  └────────────────────────────────────────────┘        │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────┬────────────────────┬───────────────────────────┘
                 │                    │
         PostgreSQL DB          Redis Channel Layer
                 │                    │
┌────────────────▼────────┐  ┌───────▼──────────┐
│   PostgreSQL (5432)     │  │  Redis (6379)    │
│                         │  │                  │
│  ┌──────────────────┐  │  │  ┌────────────┐ │
│  │  Teams           │  │  │  │  Sessions  │ │
│  │  Challenges      │  │  │  │  Cache     │ │
│  │  Submissions     │  │  │  │  Channels  │ │
│  │  FirstBloods     │  │  │  └────────────┘ │
│  └──────────────────┘  │  └──────────────────┘
└─────────────────────────┘
```

## Flujo de Datos

### 1. Envío de Flag

```
User Browser → Submit Flag Form
      ↓
  Nginx (Port 80)
      ↓
  Django View (challenges/views.py)
      ↓
  Validate Flag & Create Submission
      ↓
  Update Team Score (PostgreSQL)
      ↓
  Send WebSocket Message (Redis)
      ↓
  All Connected Clients Receive Update
      ↓
  Animate Flag Capture & Update Scoreboard
```

### 2. First Blood Detection

```
Flag Submission → Check FirstBlood.objects
      ↓
  If First to Solve:
      ↓
  Create FirstBlood Record
      ↓
  Award Bonus Points
      ↓
  Send Special WebSocket Event
      ↓
  Trigger Special Animation
      ↓
  🩸 FIRST BLOOD Alert!
```

### 3. Real-time Scoreboard

```
WebSocket Connection
      ↓
  ScoreboardConsumer.connect()
      ↓
  Join 'scoreboard' Group
      ↓
  When Flag Solved:
      ↓
  channel_layer.group_send()
      ↓
  All Clients in Group Receive
      ↓
  Update UI with Animations
```

## Stack Tecnológico

### Backend
- **Django 4.2** - Framework web principal
- **Django Channels** - WebSockets para tiempo real
- **Daphne** - Servidor ASGI
- **PostgreSQL** - Base de datos principal
- **Redis** - Cache y channel layer para WebSockets

### Frontend
- **HTML5/CSS3** - Estructura y estilos
- **JavaScript (Vanilla)** - Lógica del cliente
- **WebSocket API** - Comunicación bidireccional
- **Canvas API** - Efectos visuales (matriz, partículas)
- **CSS Animations** - Animaciones suaves

### DevOps
- **Docker** - Containerización
- **Docker Compose** - Orquestación de servicios
- **Nginx** - Reverse proxy y archivos estáticos

## Escalabilidad

### Horizontal Scaling

Para escalar horizontalmente:

1. **Multiple Web Instances**:
```yaml
web:
  deploy:
    replicas: 3
```

2. **Load Balancer** (Nginx upstream):
```nginx
upstream django {
    server web1:8000;
    server web2:8000;
    server web3:8000;
}
```

3. **Shared Redis** para mantener sincronización entre instancias

### Vertical Scaling

- Aumentar recursos de PostgreSQL
- Configurar Redis persistence
- Optimizar queries con indexes
- Implementar caching agresivo

## Seguridad

### Implementado
- ✅ CSRF Protection
- ✅ SQL Injection Protection (Django ORM)
- ✅ XSS Protection (Template escaping)
- ✅ Secure password hashing
- ✅ Environment variables para secretos

### Recomendado para Producción
- [ ] HTTPS (SSL/TLS)
- [ ] Rate limiting
- [ ] WAF (Web Application Firewall)
- [ ] Backup automático de BD
- [ ] Monitoring y logging
- [ ] Fail2ban para SSH

## Performance

### Optimizaciones Implementadas
- Static files servidos por Nginx
- WebSocket para actualizaciones eficientes
- PostgreSQL indexes en campos clave
- Redis caching para sessions

### Métricas Esperadas
- **Latencia WebSocket**: < 50ms
- **Tiempo de respuesta API**: < 200ms
- **Usuarios concurrentes**: 500+ (single instance)
- **WebSocket connections**: 1000+ (con Redis)

---

Para más información, consulta:
- **README.md** - Documentación completa
- **GUIDE.md** - Guía de uso
- **CONTRIBUTING.md** - Cómo contribuir
