from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import IntegrityError
from teams.models import Team
from challenges.models import Challenge, Category, Submission, FirstBlood

User = get_user_model()

def login_view(request):
    """Vista de login personalizada"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Verificar si el usuario existe y está inactivo
        try:
            user_obj = User.objects.get(username=username)
            if not user_obj.is_active:
                # Verificar que la contraseña sea correcta
                if user_obj.check_password(password):
                    messages.error(request, '🚫 Tu cuenta ha sido suspendida. Contacta a un administrador para más información.')
                    return render(request, 'auth/login.html')
        except User.DoesNotExist:
            pass
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'auth/login.html')

def register_view(request):
    """Vista de registro personalizada"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validaciones
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'auth/register.html')
        
        if len(password) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres')
            return render(request, 'auth/register.html')
        
        if not username or len(username) < 3:
            messages.error(request, 'El nombre de usuario debe tener al menos 3 caracteres')
            return render(request, 'auth/register.html')
        
        try:
            # Crear usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Login automático
            auth_login(request, user)
            messages.success(request, f'¡Bienvenido {username}! Tu cuenta ha sido creada exitosamente.')
            return redirect('/')
            
        except IntegrityError:
            messages.error(request, 'Este nombre de usuario ya está en uso')
        except Exception as e:
            messages.error(request, 'Error al crear la cuenta. Intenta nuevamente.')
    
    return render(request, 'auth/register.html')

def logout_view(request):
    """Vista de logout"""
    auth_logout(request)
    messages.info(request, 'Has cerrado sesión correctamente')
    return redirect('/')

def is_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    """Panel de administración personalizado"""
    context = {
        'total_users': User.objects.count(),
        'total_teams': Team.objects.count(),
        'total_challenges': Challenge.objects.count(),
        'total_submissions': Submission.objects.filter(is_correct=True).count(),
        'recent_users': User.objects.order_by('-date_joined')[:10],
        'recent_submissions': Submission.objects.select_related('team', 'challenge').order_by('-submitted_at')[:10],
    }
    return render(request, 'admin/dashboard.html', context)
