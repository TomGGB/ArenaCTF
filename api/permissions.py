"""
Permisos personalizados para la API REST
"""
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que permite lectura a todos
    pero escritura solo a administradores
    """
    def has_permission(self, request, view):
        # Permitir métodos seguros (GET, HEAD, OPTIONS) a todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permitir métodos de escritura solo a admins
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso que permite a los usuarios editar solo sus propios objetos
    o a los admins editar cualquier objeto
    """
    def has_object_permission(self, request, view, obj):
        # Los admins pueden hacer cualquier cosa
        if request.user and request.user.is_staff:
            return True
        
        # Lectura permitida para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura solo para el propietario
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsTeamMemberOrAdmin(permissions.BasePermission):
    """
    Permiso que permite acceso a miembros del equipo o admins
    """
    def has_object_permission(self, request, view, obj):
        # Los admins pueden hacer cualquier cosa
        if request.user and request.user.is_staff:
            return True
        
        # Lectura permitida para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Verificar si el usuario es miembro del equipo
        if hasattr(obj, 'members'):
            return request.user in obj.members.all()
        
        if hasattr(obj, 'team'):
            return request.user in obj.team.members.all()
        
        return False


class IsCTFActive(permissions.BasePermission):
    """
    Permiso que verifica si el CTF está activo
    """
    message = "El CTF no está activo en este momento"
    
    def has_permission(self, request, view):
        from scoreboard.models import CTFConfig
        from django.utils import timezone
        
        # Los admins siempre pueden acceder
        if request.user and request.user.is_staff:
            return True
        
        config = CTFConfig.get_config()
        
        if not config.is_active:
            return False
        
        now = timezone.now()
        
        # Verificar si el CTF ha comenzado
        if config.start_time and now < config.start_time:
            self.message = "El CTF aún no ha comenzado"
            return False
        
        # Verificar si el CTF ha terminado
        if config.end_time and now > config.end_time:
            self.message = "El CTF ha finalizado"
            return False
        
        return True


class HasTeam(permissions.BasePermission):
    """
    Permiso que verifica si el usuario pertenece a un equipo
    """
    message = "Debes pertenecer a un equipo para realizar esta acción"
    
    def has_permission(self, request, view):
        # Los admins siempre pueden acceder
        if request.user and request.user.is_staff:
            return True
        
        # Verificar si el usuario tiene equipo
        if not request.user.is_authenticated:
            return False
        
        return request.user.teams.exists()


class CanSubmitFlag(permissions.BasePermission):
    """
    Permiso combinado: CTF activo + tiene equipo
    """
    message = "No puedes enviar flags en este momento"
    
    def has_permission(self, request, view):
        # Los admins siempre pueden acceder (para testing)
        if request.user and request.user.is_staff:
            return True
        
        # Verificar CTF activo
        ctf_active = IsCTFActive()
        if not ctf_active.has_permission(request, view):
            self.message = ctf_active.message
            return False
        
        # Verificar que tiene equipo
        has_team = HasTeam()
        if not has_team.has_permission(request, view):
            self.message = has_team.message
            return False
        
        return True
