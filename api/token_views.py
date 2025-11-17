"""
Vistas adicionales para gestión de tokens de API
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from .models import APIToken


class TokenViewSet(APIView):
    """
    Vista para gestionar tokens de API (solo administradores)
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Listar tokens del usuario"""
        tokens = APIToken.objects.filter(user=request.user)
        
        token_list = []
        for token in tokens:
            token_list.append({
                'key': token.key,
                'description': token.description,
                'created_at': token.created_at,
                'last_used_at': token.last_used_at
            })
        
        return Response({'tokens': token_list})
    
    def post(self, request):
        """Crear nuevo token"""
        description = request.data.get('description', '')
        
        token = APIToken.objects.create(
            user=request.user,
            description=description
        )
        
        return Response({
            'success': True,
            'token': {
                'key': token.key,
                'description': token.description,
                'created_at': token.created_at
            }
        }, status=status.HTTP_201_CREATED)
    
    def delete(self, request):
        """Eliminar un token"""
        token_key = request.data.get('key')
        
        if not token_key:
            return Response(
                {'error': 'Se requiere el key del token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            token = APIToken.objects.get(key=token_key, user=request.user)
            token.delete()
            return Response({'success': True, 'message': 'Token eliminado'})
        except APIToken.DoesNotExist:
            return Response(
                {'error': 'Token no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
