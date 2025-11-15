# Guía de Minificación con Django Compressor

## ✅ Instalación Completada

Se ha configurado **django-compressor** para minificar automáticamente JavaScript y CSS en producción.

## 📋 Configuración Aplicada

### 1. Paquetes Instalados
- `django-compressor>=4.4` - Compresión y minificación
- `rcssmin>=1.1.1` - Minificador de CSS

### 2. Settings Configurados (`ctf_platform/settings.py`)

```python
INSTALLED_APPS = [
    ...
    'compressor',  # Agregado
    ...
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',  # Agregado
]

# Django Compressor settings
COMPRESS_ENABLED = not DEBUG  # Solo minificar en producción
COMPRESS_OFFLINE = False  # Comprimir en tiempo real
COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter', 'compressor.filters.cssmin.rCSSMinFilter']
COMPRESS_JS_FILTERS = ['compressor.filters.jsmin.JSMinFilter']
```

## 🚀 Cómo Usar en Templates

### Para JavaScript Inline:

```django
{% load static compress %}

{% compress js %}
<script>
    function myFunction() {
        console.log('Este código será minificado en producción');
        const data = { foo: 'bar', baz: 'qux' };
        return data;
    }
</script>
{% endcompress %}
```

### Para Archivos JavaScript:

```django
{% load static compress %}

{% compress js %}
<script src="{% static 'js/main.js' %}"></script>
<script src="{% static 'js/utils.js' %}"></script>
{% endcompress %}
```

### Para CSS:

```django
{% load static compress %}

{% compress css %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<style>
    body { font-family: Arial; }
</style>
{% endcompress %}
```

## 📊 Comportamiento

### En Desarrollo (DEBUG=True):
- ✅ Código **NO** se minifica
- ✅ Fácil de debuggear
- ✅ Errores legibles en consola

### En Producción (DEBUG=False):
- ✅ JavaScript minificado automáticamente
- ✅ CSS minificado automáticamente
- ✅ Reducción de ~50-70% en tamaño
- ✅ Archivos cacheables con hash único

## 🔧 Ejemplo Real: Actualizar base.html

Encuentra el bloque de JavaScript en `templates/base.html` y envuélvelo:

**Antes:**
```django
{% load static %}
<script>
    // WebSocket code here
    const ws = new WebSocket(...);
</script>
```

**Después:**
```django
{% load static compress %}
{% compress js %}
<script>
    // WebSocket code here
    const ws = new WebSocket(...);
</script>
{% endcompress %}
```

## 📝 Plantillas a Actualizar

Agrega `{% load compress %}` y envuelve JavaScript en estas plantillas:

1. ✅ `templates/base.html` - WebSocket y notificaciones
2. ✅ `templates/scoreboard/dashboard.html` - Gráficos Chart.js
3. ✅ `templates/scoreboard/public_display.html` - Display completo
4. ✅ `templates/challenges/detail.html` - Envío de flags
5. ✅ `templates/admin_panel/test_websocket.html` - Panel de testing

## ⚙️ Comandos Útiles

### Generar archivos comprimidos offline (opcional):
```bash
docker exec ctf_web python manage.py compress
```

### Limpiar caché de compressor:
```bash
docker exec ctf_web python manage.py clear_cache
```

### Recolectar archivos estáticos:
```bash
docker exec ctf_web python manage.py collectstatic --noinput
```

## 🎯 Beneficios

- **Reducción de tamaño**: 50-70% menos código
- **Mejor rendimiento**: Carga más rápida de páginas
- **Caché efectivo**: Hash único por versión
- **Sin impacto en desarrollo**: Solo activo en producción
- **Fácil de usar**: Solo agregar tags en templates

## 🚨 Notas Importantes

1. **CDN scripts**: Scripts de CDN (Tailwind, DaisyUI, Chart.js) NO necesitan compressor
2. **Inline vs Files**: Puedes comprimir tanto inline como archivos
3. **Production only**: Solo se activa cuando `DEBUG=False`
4. **No rompe código**: El minificador es seguro para JavaScript moderno

## 📦 Para Deployment

Cuando vayas a producción:

1. Asegúrate que `DEBUG=False` en `.env`
2. Los archivos se minificarán automáticamente
3. No requiere pasos adicionales

## 🔍 Verificar que Funciona

1. Abre una página con `{% compress js %}`
2. Ve el código fuente (Ctrl+U)
3. En producción verás: `<script src="/static/CACHE/js/xxxxx.js">`
4. El archivo será JavaScript minificado

## 💡 Tips

- Agrupa archivos relacionados en el mismo bloque `{% compress %}`
- No comprimas código de terceros ya minificado
- Mantén los CDN externos fuera de compress
- El compressor respeta el orden de los archivos
