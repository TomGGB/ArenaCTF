from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout, get_user_model
from django.contrib import messages

User = get_user_model()

class CheckBannedUserMiddleware:
    """Middleware para verificar si un usuario autenticado está baneado"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            # URLs permitidas para usuarios baneados
            exempt_urls = [
                reverse('login'),
                reverse('logout'),
                '/static/',
                '/media/',
            ]
            
            is_exempt = any(request.path.startswith(url) if url.startswith('/') else request.path == url for url in exempt_urls)
            
            if not is_exempt:
                logout(request)
                messages.error(request, '🚫 Tu cuenta ha sido suspendida. Contacta a un administrador para más información.')
                return redirect('login')
        
        response = self.get_response(request)
        return response

class QuickStartMiddleware:
    """Middleware para redirigir al quick start si no hay usuarios"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # URLs que no requieren el quick start
        exempt_urls = [
            reverse('quickstart:welcome'),
            reverse('quickstart:create_admin'),
            reverse('quickstart:configure_ctf'),
            reverse('quickstart:complete'),
            '/static/',
            '/media/',
        ]
        
        # Si no hay usuarios y no estamos en una URL exenta o ruta estática, redirigir al quick start
        if not User.objects.exists():
            # Verificar si es una ruta exenta
            is_exempt = any(request.path.startswith(url) if url.startswith('/') else request.path == url for url in exempt_urls)
            if not is_exempt:
                return redirect('quickstart:welcome')
        
        response = self.get_response(request)
        return response
