"""
Vista personalizada para la raíz de la API
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class APIRootView(APIView):
    """
    Vista de la raíz de la API que solo muestra información a staff
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        if not request.user.is_staff:
            return Response(
                {
                    'detail': 'API disponible. La documentación está disponible solo para administradores.',
                    'docs': 'Contacta al administrador para obtener la documentación de la API.'
                },
                status=status.HTTP_200_OK
            )
        
        # Si es staff, mostrar los endpoints disponibles
        from rest_framework.reverse import reverse
        
        return Response({
            'users': reverse('api:user-list', request=request),
            'teams': reverse('api:team-list', request=request),
            'categories': reverse('api:category-list', request=request),
            'challenges': reverse('api:challenge-list', request=request),
            'submissions': reverse('api:submission-list', request=request),
            'first-bloods': reverse('api:firstblood-list', request=request),
            'config': reverse('api:config-list', request=request),
            'scoreboard': reverse('api:scoreboard-list', request=request),
            'statistics': reverse('api:statistics-list', request=request),
            'achievements': reverse('api:achievement-list', request=request),
            'tokens': reverse('api:tokens', request=request),
            'docs': {
                'swagger': request.build_absolute_uri('/api/docs/'),
                'redoc': request.build_absolute_uri('/api/redoc/'),
                'schema': request.build_absolute_uri('/api/schema/'),
            }
        })
