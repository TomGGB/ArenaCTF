"""
URL configuration for ctf_platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api.doc_views import AdminSpectacularAPIView, AdminSpectacularSwaggerView, AdminSpectacularRedocView
from .auth_views import login_view, logout_view, register_view, admin_dashboard

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Quickstart y Admin Panel
    path('quickstart/', include('quickstart.urls')),
    path('admin-panel/', include('admin_panel.urls')),
    
    # Autenticación
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    
    # Apps principales
    path('users/', include('users.urls')),
    path('', include('scoreboard.urls')),
    path('challenges/', include('challenges.urls')),
    path('teams/', include('teams.urls')),
    
    # API REST
    path('api/', include('api.urls')),
    
    # Swagger/OpenAPI Documentation (Solo Admins)
    path('api/schema/', AdminSpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', AdminSpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', AdminSpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
