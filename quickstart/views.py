from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django.utils import timezone
from scoreboard.models import CTFConfig
from challenges.models import Category, Challenge
import os

User = get_user_model()

def welcome(request):
    """Pantalla de bienvenida del quick start"""
    # Si ya hay usuarios, redirigir al home
    if User.objects.exists():
        return redirect('scoreboard:dashboard')
    
    context = {
        'step': 1,
        'total_steps': 3,
    }
    return render(request, 'quickstart/welcome.html', context)

def create_admin(request):
    """Crear el primer usuario administrador"""
    # Si ya hay usuarios, redirigir
    if User.objects.exists():
        return redirect('scoreboard:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        
        # Validaciones
        if not username or not password:
            messages.error(request, 'Usuario y contraseña son requeridos')
            return redirect('quickstart:create_admin')
        
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('quickstart:create_admin')
        
        if len(password) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres')
            return redirect('quickstart:create_admin')
        
        # Crear usuario administrador
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            # Autenticar automáticamente
            login(request, user)
            
            messages.success(request, f'¡Bienvenido {username}! Cuenta de administrador creada exitosamente.')
            return redirect('quickstart:configure_ctf')
        
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
            return redirect('quickstart:create_admin')
    
    context = {
        'step': 2,
        'total_steps': 3,
    }
    return render(request, 'quickstart/create_admin.html', context)

def configure_ctf(request):
    """Configurar detalles del CTF"""
    # Verificar que hay al menos un usuario admin
    if not User.objects.filter(is_superuser=True).exists():
        return redirect('quickstart:create_admin')
    
    if request.method == 'POST':
        ctf_name = request.POST.get('ctf_name', 'CTF Platform').strip()
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        is_active = request.POST.get('is_active') == 'on'
        create_sample_data = request.POST.get('create_sample_data') == 'on'
        
        # Configurar CTF
        config = CTFConfig.get_config()
        config.name = ctf_name
        
        if start_time:
            config.start_time = timezone.datetime.fromisoformat(start_time)
        else:
            config.start_time = timezone.now()
        
        if end_time:
            config.end_time = timezone.datetime.fromisoformat(end_time)
        
        config.is_active = is_active
        config.save()
        
        # Crear datos de ejemplo si se solicita
        if create_sample_data:
            create_sample_challenges()
        
        messages.success(request, 'Configuración del CTF completada exitosamente')
        return redirect('quickstart:complete')
    
    context = {
        'step': 3,
        'total_steps': 3,
    }
    return render(request, 'quickstart/configure_ctf.html', context)

def complete(request):
    """Pantalla de finalización del quick start"""
    context = {
        'step': 3,
        'total_steps': 3,
    }
    return render(request, 'quickstart/complete.html', context)

def create_sample_challenges():
    """Crear categorías y challenges de ejemplo"""
    # Crear categorías
    categories_data = [
        {'name': 'Web', 'icon': '🌐', 'color': '#3b82f6'},
        {'name': 'Crypto', 'icon': '🔐', 'color': '#8b5cf6'},
        {'name': 'Forensics', 'icon': '🔍', 'color': '#10b981'},
        {'name': 'Reversing', 'icon': '⚙️', 'color': '#f59e0b'},
        {'name': 'Pwn', 'icon': '💥', 'color': '#ef4444'},
        {'name': 'Misc', 'icon': '🎲', 'color': '#6366f1'},
    ]
    
    categories = {}
    for cat_data in categories_data:
        cat, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'icon': cat_data['icon'],
                'color': cat_data['color']
            }
        )
        categories[cat_data['name']] = cat
    
    # Crear challenges de ejemplo
    challenges_data = [
        {
            'category': 'Web',
            'title': 'Basic SQL Injection',
            'description': 'Encuentra la flag en la base de datos usando SQL injection.\n\nURL: http://example.com/vuln',
            'points': 100,
            'flag': 'FLAG{sql_1nj3ct10n_b4s1c}',
        },
        {
            'category': 'Crypto',
            'title': 'Caesar Cipher',
            'description': 'Descifra el siguiente mensaje:\n\nSYNT{pnrfne_vf_rnfl}',
            'points': 50,
            'flag': 'FLAG{caesar_is_easy}',
        },
        {
            'category': 'Forensics',
            'title': 'Hidden in Plain Sight',
            'description': 'Hay algo escondido en esta imagen... ¿puedes encontrarlo?',
            'points': 150,
            'flag': 'FLAG{st3g4n0gr4phy_m4st3r}',
        },
        {
            'category': 'Reversing',
            'title': 'Simple Crackme',
            'description': 'Analiza este binario y encuentra la contraseña correcta.',
            'points': 200,
            'flag': 'FLAG{r3v3rs3_3ng1n33r1ng}',
        },
        {
            'category': 'Pwn',
            'title': 'Buffer Overflow 101',
            'description': 'Explota el buffer overflow para obtener la flag.\n\nnc example.com 1337',
            'points': 250,
            'flag': 'FLAG{buff3r_0v3rfl0w_pwn}',
        },
        {
            'category': 'Misc',
            'title': 'Welcome',
            'description': '¡Bienvenido al CTF! Esta es tu primera flag de regalo.',
            'points': 10,
            'flag': 'FLAG{w3lc0m3_t0_ctf}',
        },
    ]
    
    for chall_data in challenges_data:
        Challenge.objects.get_or_create(
            title=chall_data['title'],
            defaults={
                'category': categories[chall_data['category']],
                'description': chall_data['description'],
                'points': chall_data['points'],
                'flag': chall_data['flag'],
                'is_active': True,
            }
        )
