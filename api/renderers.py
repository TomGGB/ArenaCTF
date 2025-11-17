"""
Renderers personalizados para la API
"""
from rest_framework.renderers import BrowsableAPIRenderer


class StaffBrowsableAPIRenderer(BrowsableAPIRenderer):
    """
    Renderer que solo muestra la interfaz navegable de DRF a usuarios staff
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        request = renderer_context.get('request') if renderer_context else None
        
        # Si el usuario no es staff, no renderizar la interfaz navegable
        if request and not (request.user and request.user.is_staff):
            return None
        
        # Si es staff, renderizar normalmente
        return super().render(data, accepted_media_type, renderer_context)
