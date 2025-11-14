from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Challenges
    path('challenges/', views.challenges_list, name='challenges_list'),
    path('challenges/create/', views.challenge_create, name='challenge_create'),
    path('challenges/<uuid:challenge_id>/edit/', views.challenge_edit, name='challenge_edit'),
    path('challenges/<uuid:challenge_id>/delete/', views.challenge_delete, name='challenge_delete'),
    
    # Categories
    path('categories/', views.categories_list, name='categories_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<uuid:category_id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<uuid:category_id>/delete/', views.category_delete, name='category_delete'),
    
    # Teams
    path('teams/', views.teams_list, name='teams_list'),
    path('teams/create/', views.team_create, name='team_create'),
    path('teams/<uuid:team_id>/', views.team_detail, name='team_detail'),
    path('teams/<uuid:team_id>/edit/', views.team_edit, name='team_edit'),
    path('teams/<uuid:team_id>/delete/', views.team_delete, name='team_delete'),
    
    # Users
    path('users/', views.users_list, name='users_list'),
    path('users/<uuid:user_id>/', views.user_detail, name='user_detail'),
    path('users/<uuid:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<uuid:user_id>/ban/', views.user_ban, name='user_ban'),
    path('users/<uuid:user_id>/delete/', views.user_delete, name='user_delete'),
    
    # CTF Config
    path('config/', views.ctf_config, name='ctf_config'),
    
    # Submissions
    path('submissions/', views.submissions_list, name='submissions_list'),
]
