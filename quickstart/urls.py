from django.urls import path
from . import views

app_name = 'quickstart'

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('create-admin/', views.create_admin, name='create_admin'),
    path('configure-ctf/', views.configure_ctf, name='configure_ctf'),
    path('complete/', views.complete, name='complete'),
]
