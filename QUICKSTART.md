# 🚀 INICIO RÁPIDO - CTF ARENA

## Para Windows (PowerShell o CMD)

```cmd
start.bat
```

## Para Linux/Mac

```bash
chmod +x start.sh
./start.sh
```

---

## Acceso Rápido

Una vez iniciado, accede a:

- **🌐 Frontend**: http://localhost
- **⚙️ Admin Panel**: http://localhost/admin
  - Usuario: `admin`
  - Contraseña: `admin123`

---

## Comandos Útiles

### Ver logs
```bash
docker-compose logs -f
```

### Detener servicios
```bash
docker-compose down
```

### Reiniciar
```bash
docker-compose restart
```

### Crear nuevo superusuario
```bash
docker-compose exec web python manage.py createsuperuser
```

### Inicializar datos de ejemplo
```bash
docker-compose exec web python manage.py init_data
```

---

## 📚 Documentación Completa

- **README.md** - Documentación completa del proyecto
- **GUIDE.md** - Guía detallada de uso
- **CONTRIBUTING.md** - Guía para contribuir

---

**¡Disfruta tu CTF! 🎮🏆**
