from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('', views.team_list, name='team_list'),
    path('list/', views.all_teams_list, name='list'),
    path('register/', views.team_register, name='register'),
    path('join/', views.team_join, name='join'),
    path('<uuid:team_id>/', views.team_detail, name='team_detail'),
    path('<uuid:team_id>/leave/', views.team_leave, name='leave'),
]
