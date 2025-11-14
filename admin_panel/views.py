from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from challenges.models import Challenge, Category, Submission, FirstBlood
from teams.models import Team
from scoreboard.models import CTFConfig

User = get_user_model()

def is_admin(user):
    """Verificar si el usuario es administrador"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_admin)
def dashboard(request):
    """Dashboard principal del panel de administración"""
    # Estadísticas generales
    total_users = User.objects.count()
    total_teams = Team.objects.count()
    total_challenges = Challenge.objects.count()
    total_categories = Category.objects.count()
    total_submissions = Submission.objects.count()
    correct_submissions = Submission.objects.filter(is_correct=True).count()
    total_first_bloods = FirstBlood.objects.count()
    
    # Actividad reciente
    recent_submissions = Submission.objects.select_related(
        'team', 'challenge', 'submitted_by'
    ).order_by('-submitted_at')[:10]
    
    recent_teams = Team.objects.order_by('-created_at')[:5]
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Configuración del CTF
    ctf_config = CTFConfig.get_config()
    
    # Challenges por categoría
    challenges_by_category = Category.objects.annotate(
        challenge_count=Count('challenges')
    ).order_by('-challenge_count')
    
    # Top equipos
    top_teams = Team.objects.order_by('-total_score')[:5]
    
    context = {
        'total_users': total_users,
        'total_teams': total_teams,
        'total_challenges': total_challenges,
        'total_categories': total_categories,
        'total_submissions': total_submissions,
        'correct_submissions': correct_submissions,
        'total_first_bloods': total_first_bloods,
        'recent_submissions': recent_submissions,
        'recent_teams': recent_teams,
        'recent_users': recent_users,
        'ctf_config': ctf_config,
        'challenges_by_category': challenges_by_category,
        'top_teams': top_teams,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)

# === CHALLENGES ===

@user_passes_test(is_admin)
def challenges_list(request):
    """Lista de todos los challenges"""
    challenges = Challenge.objects.select_related('category').annotate(
        solve_count=Count('submissions', filter=Q(submissions__is_correct=True))
    ).order_by('-created_at')
    
    context = {
        'challenges': challenges,
    }
    return render(request, 'admin_panel/challenges/list.html', context)

@user_passes_test(is_admin)
def challenge_create(request):
    """Crear un nuevo challenge"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        points = request.POST.get('points')
        flag = request.POST.get('flag')
        hints = request.POST.get('hints', '')
        is_active = request.POST.get('is_active') == 'on'
        
        try:
            category = Category.objects.get(id=category_id)
            challenge = Challenge.objects.create(
                title=title,
                description=description,
                category=category,
                points=int(points),
                flag=flag,
                hints=hints,
                is_active=is_active
            )
            messages.success(request, f'Challenge "{title}" creado exitosamente')
            return redirect('admin_panel:challenges_list')
        except Exception as e:
            messages.error(request, f'Error al crear challenge: {str(e)}')
    
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'admin_panel/challenges/create.html', context)

@user_passes_test(is_admin)
def challenge_edit(request, challenge_id):
    """Editar un challenge existente"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    if request.method == 'POST':
        challenge.title = request.POST.get('title')
        challenge.description = request.POST.get('description')
        challenge.category_id = request.POST.get('category')
        challenge.points = int(request.POST.get('points'))
        challenge.flag = request.POST.get('flag')
        challenge.hints = request.POST.get('hints', '')
        challenge.is_active = request.POST.get('is_active') == 'on'
        
        try:
            challenge.save()
            messages.success(request, f'Challenge "{challenge.title}" actualizado')
            return redirect('admin_panel:challenges_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
    
    # Estadísticas del challenge
    solve_count = Submission.objects.filter(challenge=challenge, is_correct=True).values('submitted_by').distinct().count()
    has_first_blood = FirstBlood.objects.filter(challenge=challenge).exists()
    total_attempts = Submission.objects.filter(challenge=challenge).count()
    solve_rate = round((solve_count / total_attempts * 100) if total_attempts > 0 else 0, 1)
    
    categories = Category.objects.all()
    context = {
        'challenge': challenge,
        'categories': categories,
        'solve_count': solve_count,
        'has_first_blood': has_first_blood,
        'solve_rate': solve_rate,
    }
    return render(request, 'admin_panel/challenges/edit.html', context)

@user_passes_test(is_admin)
def challenge_delete(request, challenge_id):
    """Eliminar un challenge"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    if request.method == 'POST':
        title = challenge.title
        challenge.delete()
        messages.success(request, f'Challenge "{title}" eliminado')
        return redirect('admin_panel:challenges_list')
    
    # Estadísticas
    submission_count = Submission.objects.filter(challenge=challenge).count()
    has_first_blood = FirstBlood.objects.filter(challenge=challenge).exists()
    
    context = {
        'challenge': challenge,
        'submission_count': submission_count,
        'has_first_blood': has_first_blood,
    }
    return render(request, 'admin_panel/challenges/delete.html', context)

# === CATEGORIES ===

@user_passes_test(is_admin)
def categories_list(request):
    """Lista de categorías"""
    categories = Category.objects.annotate(
        challenge_count=Count('challenges')
    ).order_by('name')
    
    context = {'categories': categories}
    return render(request, 'admin_panel/categories/list.html', context)

@user_passes_test(is_admin)
def category_create(request):
    """Crear una nueva categoría"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        try:
            # Los campos icon y color usan sus valores por defecto del modelo
            category = Category.objects.create(
                name=name,
                description=description
            )
            messages.success(request, f'Categoría "{name}" creada exitosamente')
            return redirect('admin_panel:categories_list')
        except Exception as e:
            messages.error(request, f'Error al crear categoría: {str(e)}')
    
    return render(request, 'admin_panel/categories/create.html')

@user_passes_test(is_admin)
def category_edit(request, category_id):
    """Editar una categoría"""
    from django.db.models import Sum
    
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description', '')
        
        try:
            category.save()
            messages.success(request, f'Categoría "{category.name}" actualizada')
            return redirect('admin_panel:categories_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
    
    # Estadísticas
    active_challenges_count = Challenge.objects.filter(category=category, is_active=True).count()
    total_solves = Submission.objects.filter(
        challenge__category=category, 
        is_correct=True
    ).values('challenge').distinct().count()
    
    context = {
        'category': category,
        'active_challenges_count': active_challenges_count,
        'total_solves': total_solves,
    }
    return render(request, 'admin_panel/categories/edit.html', context)

@user_passes_test(is_admin)
def category_delete(request, category_id):
    """Eliminar una categoría"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Categoría "{name}" eliminada')
        return redirect('admin_panel:categories_list')
    
    context = {'category': category}
    return render(request, 'admin_panel/categories/delete.html', context)

# === TEAMS ===

@user_passes_test(is_admin)
def teams_list(request):
    """Lista de equipos"""
    teams = Team.objects.prefetch_related('members').order_by('-total_score')
    
    # Calcular total de miembros
    total_members = User.objects.filter(teams__isnull=False).distinct().count()
    
    # Promedio de miembros por equipo
    avg_members_per_team = total_members / teams.count() if teams.count() > 0 else 0
    
    context = {
        'teams': teams,
        'total_members': total_members,
        'avg_members_per_team': avg_members_per_team,
    }
    return render(request, 'admin_panel/teams/list.html', context)

@user_passes_test(is_admin)
def team_detail(request, team_id):
    """Detalles de un equipo"""
    from django.db.models import Sum
    
    team = get_object_or_404(Team, id=team_id)
    members = team.members.all()
    
    # Submissions y first bloods
    submissions = Submission.objects.filter(team=team).select_related(
        'challenge__category', 'submitted_by'
    ).order_by('-submitted_at')
    
    first_bloods = FirstBlood.objects.filter(team=team).select_related(
        'challenge__category', 'achieved_by'
    )
    
    # Challenges resueltos
    solved_challenges = Challenge.objects.filter(
        submissions__team=team,
        submissions__is_correct=True
    ).distinct()
    
    # First bloods challenges
    first_bloods_challenges = [fb.challenge for fb in first_bloods]
    
    # Estadísticas de miembros
    member_stats = []
    for member in members:
        member_submissions = Submission.objects.filter(
            team=team,
            submitted_by=member,
            is_correct=True
        )
        member_solves = member_submissions.values('challenge').distinct().count()
        member_points = member_submissions.aggregate(total=Sum('challenge__points'))['total'] or 0
        
        member_first_bloods = first_bloods.filter(achieved_by=member).count()
        member_fb_points = first_bloods.filter(achieved_by=member).aggregate(
            total=Sum('challenge__points')
        )['total'] or 0
        
        member_stats.append({
            'member': member,
            'solves': member_solves,
            'total_points': member_points + member_fb_points,
            'first_bloods': member_first_bloods,
        })
    
    # Ordenar por puntos
    member_stats.sort(key=lambda x: x['total_points'], reverse=True)
    
    # Progreso por categoría
    categories = Category.objects.all()
    categories_progress = {}
    for category in categories:
        cat_challenges = Challenge.objects.filter(category=category, is_active=True).count()
        cat_solved = solved_challenges.filter(category=category).count()
        
        if cat_challenges > 0:
            categories_progress[category.name] = {
                'total': cat_challenges,
                'solved': cat_solved,
            }
    
    context = {
        'team': team,
        'member_stats': member_stats,
        'submissions': submissions,
        'first_bloods': first_bloods,
        'solved_challenges': solved_challenges,
        'first_bloods_challenges': first_bloods_challenges,
        'categories_progress': categories_progress,
    }
    return render(request, 'admin_panel/teams/detail.html', context)

@user_passes_test(is_admin)
def team_delete(request, team_id):
    """Eliminar un equipo"""
    team = get_object_or_404(Team, id=team_id)
    
    if request.method == 'POST':
        confirm_name = request.POST.get('confirm_name', '')
        if confirm_name == team.name:
            name = team.name
            team.delete()
            messages.success(request, f'Equipo "{name}" eliminado')
            return redirect('admin_panel:teams_list')
        else:
            messages.error(request, 'El nombre del equipo no coincide')
    
    # Estadísticas para el template
    submission_count = Submission.objects.filter(team=team).count()
    first_blood_count = FirstBlood.objects.filter(team=team).count()
    solved_count = Submission.objects.filter(team=team, is_correct=True).values('challenge').distinct().count()
    has_first_blood = first_blood_count > 0
    
    context = {
        'team': team,
        'submission_count': submission_count,
        'first_blood_count': first_blood_count,
        'solved_count': solved_count,
        'has_first_blood': has_first_blood,
    }
    return render(request, 'admin_panel/teams/delete.html', context)

# === USERS ===

@user_passes_test(is_admin)
def users_list(request):
    """Lista de usuarios"""
    from django.db.models import Sum
    
    users = User.objects.prefetch_related('teams').order_by('-date_joined')
    
    # Añadir estadísticas a cada usuario
    for user in users:
        # Puntos totales (submissions correctas)
        user.get_total_points = Submission.objects.filter(
            submitted_by=user, is_correct=True
        ).aggregate(total=Sum('challenge__points'))['total'] or 0
        
        # First bloods bonus
        fb_points = FirstBlood.objects.filter(
            achieved_by=user
        ).aggregate(total=Sum('bonus_points'))['total'] or 0
        user.get_total_points += fb_points
        
        # Solves count
        user.get_solved_count = Submission.objects.filter(
            submitted_by=user, is_correct=True
        ).values('challenge').distinct().count()
    
    # Estadísticas generales
    admin_count = users.filter(Q(is_staff=True) | Q(is_superuser=True)).count()
    users_in_teams = users.exclude(teams__isnull=True).distinct().count()
    users_without_team = users.filter(teams__isnull=True).count()
    
    # Top 5 usuarios
    top_users = sorted(users, key=lambda u: u.get_total_points, reverse=True)[:5]
    
    # Usuarios activos (con al menos 1 submission)
    active_users = User.objects.filter(submissions__isnull=False).distinct().count()
    active_users_percentage = round((active_users / users.count() * 100) if users.count() > 0 else 0, 1)
    
    # Promedio de puntos
    total_points = sum(u.get_total_points for u in users)
    avg_points = total_points / users.count() if users.count() > 0 else 0
    
    # Último usuario registrado
    latest_user = users.first() if users.exists() else None
    
    context = {
        'users': users,
        'admin_count': admin_count,
        'users_in_teams': users_in_teams,
        'users_without_team': users_without_team,
        'top_users': top_users,
        'active_users': active_users,
        'active_users_percentage': active_users_percentage,
        'avg_points': avg_points,
        'latest_user': latest_user,
    }
    return render(request, 'admin_panel/users/list.html', context)

@user_passes_test(is_admin)
def user_detail(request, user_id):
    """Detalles de un usuario"""
    from django.db.models import Sum
    
    user = get_object_or_404(User, id=user_id)
    
    # Submissions del usuario
    all_submissions = Submission.objects.filter(submitted_by=user).select_related(
        'challenge__category', 'team'
    ).order_by('-submitted_at')
    
    recent_submissions = all_submissions[:20]
    total_submissions = all_submissions.count()
    
    # Challenges resueltos
    solved_challenges = Submission.objects.filter(
        submitted_by=user, is_correct=True
    ).select_related('challenge__category').order_by('-submitted_at')
    
    solved_count = solved_challenges.values('challenge').distinct().count()
    
    # Puntos totales
    total_points = solved_challenges.aggregate(
        total=Sum('challenge__points')
    )['total'] or 0
    
    # First bloods
    first_bloods = FirstBlood.objects.filter(achieved_by=user).select_related(
        'challenge__category'
    )
    first_bloods_count = first_bloods.count()
    
    # Agregar puntos bonus de first bloods
    fb_bonus = first_bloods.aggregate(total=Sum('bonus_points'))['total'] or 0
    total_points += fb_bonus
    
    # IDs de challenges con first blood
    first_blood_challenges = list(first_bloods.values_list('challenge__id', flat=True))
    
    # Progreso por categoría
    categories = Category.objects.all()
    categories_progress = {}
    for category in categories:
        cat_challenges = Challenge.objects.filter(category=category, is_active=True).count()
        cat_solved = solved_challenges.filter(challenge__category=category).values('challenge').distinct().count()
        cat_points = solved_challenges.filter(challenge__category=category).aggregate(
            total=Sum('challenge__points')
        )['total'] or 0
        
        if cat_challenges > 0:
            categories_progress[category.name] = {
                'total': cat_challenges,
                'solved': cat_solved,
                'points': cat_points,
            }
    
    context = {
        'user': user,
        'total_points': total_points,
        'solved_count': solved_count,
        'first_bloods_count': first_bloods_count,
        'total_submissions': total_submissions,
        'solved_challenges': solved_challenges,
        'first_bloods': first_bloods,
        'first_blood_challenges': first_blood_challenges,
        'recent_submissions': recent_submissions,
        'categories_progress': categories_progress,
    }
    return render(request, 'admin_panel/users/detail.html', context)

# === CTF CONFIG ===

@user_passes_test(is_admin)
def ctf_config(request):
    """Configuración del CTF"""
    config = CTFConfig.get_config()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        first_blood_points = request.POST.get('first_blood_points')
        timezone_str = request.POST.get('timezone')
        
        if name:
            config.name = name
        if start_time:
            config.start_time = timezone.datetime.fromisoformat(start_time)
        if end_time:
            config.end_time = timezone.datetime.fromisoformat(end_time)
        if first_blood_points:
            config.first_blood_points = int(first_blood_points)
        if timezone_str:
            config.timezone = timezone_str
        
        config.save()
        
        messages.success(request, 'Configuración actualizada exitosamente')
        return redirect('admin_panel:ctf_config')
    
    # Estado del CTF
    now = timezone.now()
    is_active = config.start_time <= now <= config.end_time if config.start_time and config.end_time else False
    is_upcoming = now < config.start_time if config.start_time else False
    
    # Tiempos
    if is_active and config.end_time:
        time_remaining = config.end_time - now
        time_remaining = f"{time_remaining.days} días, {time_remaining.seconds // 3600} horas"
    else:
        time_remaining = None
    
    if is_upcoming and config.start_time:
        time_until_start = config.start_time - now
        time_until_start = f"{time_until_start.days} días, {time_until_start.seconds // 3600} horas"
    else:
        time_until_start = None
    
    # Duración
    if config.start_time and config.end_time:
        duration = config.end_time - config.start_time
        duration = f"{duration.days} días, {duration.seconds // 3600} horas"
    else:
        duration = "No configurado"
    
    # Estadísticas
    total_challenges = Challenge.objects.count()
    total_teams = Team.objects.count()
    total_users = User.objects.count()
    total_submissions = Submission.objects.count()
    
    context = {
        'config': config,
        'is_active': is_active,
        'is_upcoming': is_upcoming,
        'time_remaining': time_remaining,
        'time_until_start': time_until_start,
        'duration': duration,
        'total_challenges': total_challenges,
        'total_teams': total_teams,
        'total_users': total_users,
        'total_submissions': total_submissions,
    }
    return render(request, 'admin_panel/config.html', context)

# === SUBMISSIONS ===

@user_passes_test(is_admin)
def submissions_list(request):
    """Lista de submissions"""
    from django.db.models import Count
    
    submissions = Submission.objects.select_related(
        'team', 'challenge__category', 'submitted_by'
    ).order_by('-submitted_at')
    
    # Agregar campo is_first_blood a cada submission
    first_blood_ids = FirstBlood.objects.values_list('challenge_id', flat=True)
    for submission in submissions:
        submission.is_first_blood = submission.challenge_id in first_blood_ids and submission.is_correct
    
    # Estadísticas
    total_submissions = submissions.count()
    correct_submissions = submissions.filter(is_correct=True).count()
    incorrect_submissions = total_submissions - correct_submissions
    success_rate = round((correct_submissions / total_submissions * 100) if total_submissions > 0 else 0, 1)
    
    # Challenges más intentados
    most_attempted = submissions.values(
        'challenge__title', 
        'challenge__category__name'
    ).annotate(
        total=Count('id'),
        correct=Count('id', filter=Q(is_correct=True))
    ).order_by('-total')[:5]
    
    # Actividad reciente (últimas 10)
    recent_submissions = submissions[:10]
    
    context = {
        'submissions': submissions[:100],  # Limitar a 100 para performance
        'total_submissions': total_submissions,
        'correct_submissions': correct_submissions,
        'incorrect_submissions': incorrect_submissions,
        'success_rate': success_rate,
        'most_attempted': most_attempted,
        'recent_submissions': recent_submissions,
    }
    return render(request, 'admin_panel/submissions.html', context)

# === USER MANAGEMENT ===

@user_passes_test(is_admin)
def user_edit(request, user_id):
    """Editar usuario"""
    user = get_object_or_404(User, id=user_id)
    teams = Team.objects.all()
    
    if request.method == 'POST':
        # Actualizar datos básicos
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        
        # Permisos
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_superuser = request.POST.get('is_superuser') == 'on'
        user.is_active = request.POST.get('is_active') == 'on'
        
        # Cambiar contraseña si se proporciona
        new_password = request.POST.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        try:
            user.save()
            
            # Actualizar equipo
            team_id = request.POST.get('team')
            if team_id:
                team = get_object_or_404(Team, id=team_id)
                # Limpiar equipos anteriores
                user.teams.clear()
                # Agregar al nuevo equipo
                team.members.add(user)
            elif request.POST.get('remove_team') == 'on':
                user.teams.clear()
            
            messages.success(request, f'Usuario "{user.username}" actualizado exitosamente')
            return redirect('admin_panel:user_detail', user_id=user.id)
        except Exception as e:
            messages.error(request, f'Error al actualizar usuario: {str(e)}')
    
    context = {
        'user_obj': user,
        'teams': teams,
    }
    return render(request, 'admin_panel/users/edit.html', context)

@user_passes_test(is_admin)
def user_ban(request, user_id):
    """Banear/desbanear usuario"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        
        status = "desbaneado" if user.is_active else "baneado"
        messages.success(request, f'Usuario "{user.username}" {status} exitosamente')
        return redirect('admin_panel:user_detail', user_id=user.id)
    
    context = {'user_obj': user}
    return render(request, 'admin_panel/users/ban.html', context)

@user_passes_test(is_admin)
def user_delete(request, user_id):
    """Eliminar usuario"""
    user = get_object_or_404(User, id=user_id)
    
    # No permitir eliminar al propio usuario
    if user.id == request.user.id:
        messages.error(request, 'No puedes eliminar tu propia cuenta')
        return redirect('admin_panel:users_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Usuario "{username}" eliminado exitosamente')
        return redirect('admin_panel:users_list')
    
    # Estadísticas del usuario
    submission_count = Submission.objects.filter(submitted_by=user).count()
    first_blood_count = FirstBlood.objects.filter(achieved_by=user).count()
    
    context = {
        'user_obj': user,
        'submission_count': submission_count,
        'first_blood_count': first_blood_count,
    }
    return render(request, 'admin_panel/users/delete.html', context)

# === TEAM MANAGEMENT ===

@user_passes_test(is_admin)
def team_edit(request, team_id):
    """Editar equipo"""
    team = get_object_or_404(Team, id=team_id)
    available_users = User.objects.exclude(teams=team)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_info':
            # Actualizar información básica
            team.name = request.POST.get('name', team.name)
            team.color = request.POST.get('color', team.color)
            
            try:
                team.save()
                messages.success(request, f'Equipo "{team.name}" actualizado exitosamente')
            except Exception as e:
                messages.error(request, f'Error al actualizar equipo: {str(e)}')
        
        elif action == 'add_member':
            # Agregar miembro
            user_id = request.POST.get('user_id')
            if user_id:
                user = get_object_or_404(User, id=user_id)
                team.members.add(user)
                messages.success(request, f'Usuario "{user.username}" agregado al equipo')
        
        elif action == 'remove_member':
            # Remover miembro
            user_id = request.POST.get('user_id')
            if user_id:
                user = get_object_or_404(User, id=user_id)
                team.members.remove(user)
                messages.success(request, f'Usuario "{user.username}" removido del equipo')
        
        elif action == 'reset_score':
            # Resetear puntaje
            team.total_score = 0
            team.save()
            messages.success(request, f'Puntaje del equipo "{team.name}" reseteado')
        
        return redirect('admin_panel:team_edit', team_id=team.id)
    
    context = {
        'team': team,
        'available_users': available_users,
    }
    return render(request, 'admin_panel/teams/edit.html', context)

@user_passes_test(is_admin)
def team_create(request):
    """Crear nuevo equipo"""
    if request.method == 'POST':
        name = request.POST.get('name')
        color = request.POST.get('color', '#FF0000')
        
        try:
            team = Team.objects.create(name=name, color=color)
            messages.success(request, f'Equipo "{name}" creado exitosamente')
            return redirect('admin_panel:team_detail', team_id=team.id)
        except Exception as e:
            messages.error(request, f'Error al crear equipo: {str(e)}')
    
    return render(request, 'admin_panel/teams/create.html')
