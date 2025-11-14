from django.urls import path
from . import views

app_name = 'challenges'

urlpatterns = [
    path('', views.challenge_list, name='list'),
    path('<uuid:challenge_id>/', views.challenge_detail, name='detail'),
    path('<uuid:challenge_id>/submit/', views.submit_flag, name='submit'),
]
