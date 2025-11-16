"""
URL configuration for ctf_platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .auth_views import login_view, logout_view, register_view, admin_dashboard

urlpatterns = [
    path('quickstart/', include('quickstart.urls')),
    path('admin-panel/', include('admin_panel.urls')),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('users/', include('users.urls')),
    path('', include('scoreboard.urls')),
    path('challenges/', include('challenges.urls')),
    path('teams/', include('teams.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
