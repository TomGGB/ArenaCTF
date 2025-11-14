from django.urls import path
from . import views

app_name = 'scoreboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('display/', views.public_display, name='public_display'),
    path('api/scoreboard/', views.get_scoreboard_data, name='api_scoreboard'),
    path('api/display/', views.get_display_data, name='api_display'),
]
