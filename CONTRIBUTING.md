# Contributing to CTF ARENA

¡Gracias por tu interés en contribuir a CTF ARENA! 🎮

## 🎯 Cómo Contribuir

### Reportar Bugs

1. Verifica que el bug no esté ya reportado en Issues
2. Crea un nuevo Issue con:
   - Descripción clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Screenshots si aplica
   - Logs relevantes

### Proponer Features

1. Abre un Issue con la etiqueta "enhancement"
2. Describe claramente la funcionalidad
3. Explica por qué sería útil
4. Proporciona ejemplos de uso

### Pull Requests

1. Fork el repositorio
2. Crea una rama para tu feature:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Haz tus cambios siguiendo las guías de estilo
4. Commit con mensajes descriptivos:
   ```bash
   git commit -m "Add: Implementa sistema de hints"
   ```
5. Push a tu fork:
   ```bash
   git push origin feature/amazing-feature
   ```
6. Abre un Pull Request

## 📝 Guías de Estilo

### Python

- Seguir PEP 8
- Usar docstrings para funciones y clases
- Mantener funciones pequeñas y focalizadas
- Nombres descriptivos en español o inglés consistentes

### HTML/CSS

- Indentación de 4 espacios
- Clases descriptivas en kebab-case
- Comentarios para secciones complejas
- CSS organizado por componentes

### JavaScript

- Usar ES6+ features
- Nombres de variables en camelCase
- Funciones con nombres descriptivos
- Comentarios JSDoc cuando sea necesario

### Commits

Formato: `Tipo: Descripción corta`

Tipos:
- `Add`: Nueva funcionalidad
- `Fix`: Corrección de bug
- `Update`: Actualización de funcionalidad existente
- `Remove`: Eliminación de código
- `Refactor`: Refactorización de código
- `Docs`: Cambios en documentación
- `Style`: Cambios de formato/estilo

Ejemplos:
```
Add: Sistema de badges por logros
Fix: Error en cálculo de puntos first blood
Update: Mejora animaciones del scoreboard
Docs: Actualiza guía de instalación
```

## 🧪 Testing

Antes de hacer un PR:

```bash
# Ejecutar tests
docker-compose exec web python manage.py test

# Verificar PEP 8
docker-compose exec web flake8 .

# Verificar migraciones
docker-compose exec web python manage.py makemigrations --check
```

## 🌟 Ideas para Contribuir

- [ ] Sistema de hints con penalización de puntos
- [ ] Gráficas de progreso por equipo
- [ ] Chat en tiempo real entre participantes
- [ ] Sistema de logros y badges
- [ ] API REST completa con documentación
- [ ] Modo torneo con eliminación por rounds
- [ ] Integración con Discord/Slack
- [ ] Sistema de replays para revisar el CTF
- [ ] Exportación de estadísticas a CSV/JSON
- [ ] Dashboard de analytics avanzado
- [ ] Modo "King of the Hill"
- [ ] Challenges dinámicos (se generan al acceder)
- [ ] Sistema de reporte de problemas en challenges
- [ ] Modo dark/light theme
- [ ] Internacionalización (i18n)

## 📞 Contacto

- GitHub Issues: Para bugs y features
- Discussions: Para preguntas generales

---

¡Gracias por hacer CTF ARENA mejor! 🚀
