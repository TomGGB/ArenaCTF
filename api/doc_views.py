"""
Vistas personalizadas para documentación de API con restricción de acceso
"""
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


def is_admin(user):
    """Verifica si el usuario es administrador"""
    return user.is_authenticated and user.is_staff


@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminSpectacularAPIView(SpectacularAPIView):
    """Schema de API solo para administradores"""
    pass


@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminSpectacularSwaggerView(SpectacularSwaggerView):
    """Swagger UI solo para administradores"""
    pass


@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminSpectacularRedocView(SpectacularRedocView):
    """ReDoc solo para administradores"""
    pass
