"""
Autenticación personalizada para la API
Incluye soporte para tokens de usuario
"""
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model

User = get_user_model()


class APITokenAuthentication(TokenAuthentication):
    """
    Autenticación personalizada con tokens
    Compatible con CTFd API
    """
    keyword = 'Token'
    
    def authenticate_credentials(self, key):
        """Autenticar usando el token"""
        from .models import APIToken
        
        try:
            token = APIToken.objects.select_related('user').get(key=key)
        except APIToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Token inválido')
        
        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('Usuario inactivo o eliminado')
        
        # Actualizar último uso
        token.update_last_used()
        
        return (token.user, token)
