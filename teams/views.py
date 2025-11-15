from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from .models import Team
from challenges.models import Challenge, Submission, FirstBlood
from scoreboard.models import Achievement

def team_register(request):
    """Vista para registro de equipos"""
    if request.method == 'POST':
        name = request.POST.get('name')
        color = request.POST.get('color', '#00FF41')
        
        team = Team.objects.create(name=name, color=color)
        
        # Agregar al usuario que creó el equipo automáticamente
        if request.user.is_authenticated:
            team.members.add(request.user)
        
        messages.success(request, f'¡Equipo "{name}" creado exitosamente y te has unido!')
        return redirect('scoreboard:dashboard')
    
    return render(request, 'teams/register.html')

def team_list(request):
    """Vista principal de equipos - redirige al equipo del usuario"""
    # Si el usuario tiene equipo, redirigir a su equipo
    if request.user.is_authenticated:
        user_team = request.user.teams.first()
        if user_team:
            return redirect('teams:team_detail', team_id=user_team.id)
    
    # Si no tiene equipo, mostrar lista de equipos
    teams = Team.objects.all().order_by('-total_score')
    return render(request, 'teams/list.html', {'teams': teams})

def all_teams_list(request):
    """Vista para ver todos los equipos"""
    teams = Team.objects.all().order_by('-total_score')
    
    # Obtener el equipo del usuario si lo tiene
    user_team = None
    if request.user.is_authenticated:
        user_team = request.user.teams.first()
    
    return render(request, 'teams/all_teams.html', {
        'teams': teams,
        'user_team': user_team
    })

def team_detail(request, team_id):
    """Vista para ver los detalles de un equipo"""
    team = get_object_or_404(Team, id=team_id)
    
    # Obtener challenges resueltos (submissions correctos)
    solved_challenges = Submission.objects.filter(
        team=team,
        is_correct=True
    ).select_related('challenge', 'challenge__category').order_by('-submitted_at')
    
    # Todos los intentos (correctos e incorrectos)
    all_submissions = Submission.objects.filter(
        team=team
    ).select_related('challenge').order_by('-submitted_at')[:50]  # Últimos 50
    
    # First bloods del equipo
    first_bloods = FirstBlood.objects.filter(team=team).select_related('challenge')
    
    # Estadísticas
    total_challenges = Challenge.objects.count()
    solved_count = solved_challenges.count()
    first_bloods_count = first_bloods.count()
    first_bloods_points = sum(fb.bonus_points for fb in first_bloods)
    
    # Última submission
    last_submission = all_submissions.first() if all_submissions else None
    
    # Ranking del equipo
    all_teams = Team.objects.all().order_by('-total_score')
    rank = list(all_teams).index(team) + 1 if team in all_teams else 0
    
    # Estadísticas por miembro
    member_stats = []
    for member in team.members.all():
        # Submissions correctos del miembro
        member_submissions = solved_challenges.filter(submitted_by=member)
        member_points = sum(sub.challenge.points for sub in member_submissions)
        
        # First bloods del miembro
        member_first_bloods = first_bloods.filter(achieved_by=member)
        member_fb_points = sum(fb.bonus_points for fb in member_first_bloods)
        
        # Logros individuales del miembro
        member_achievements = Achievement.objects.filter(
            user=member,
            category='individual'
        ).order_by('-earned_at')
        
        # Añadir información del logro
        for achievement in member_achievements:
            achievement.info = achievement.get_info()
        
        member_stats.append({
            'user': member,
            'submissions_count': member_submissions.count(),
            'points': member_points,
            'first_bloods_count': member_first_bloods.count(),
            'first_bloods_points': member_fb_points,
            'total_points': member_points + member_fb_points,
            'achievements': member_achievements,
        })
    
    # Ordenar miembros por puntos totales
    member_stats.sort(key=lambda x: x['total_points'], reverse=True)
    
    # Progreso por categoría
    from challenges.models import Category
    categories = Category.objects.all()
    category_stats = []
    
    for category in categories:
        total = Challenge.objects.filter(category=category).count()
        solved = solved_challenges.filter(challenge__category=category).count()
        category_stats.append({
            'name': category.name,
            'icon': category.icon,
            'total': total,
            'solved': solved
        })
    
    # Logros del equipo
    team_achievements = Achievement.objects.filter(
        team=team,
        category='team'
    ).order_by('-earned_at')
    
    # Añadir información del logro a cada objeto
    for achievement in team_achievements:
        achievement.info = achievement.get_info()
    
    # Verificar si el usuario puede ver el código de invitación
    can_view_invite_code = (
        request.user.is_authenticated and 
        (request.user in team.members.all() or request.user.is_staff or request.user.is_superuser)
    )
    
    context = {
        'team': team,
        'solved_challenges': solved_challenges,
        'all_submissions': all_submissions,
        'first_bloods': first_bloods,
        'total_challenges': total_challenges,
        'solved_count': solved_count,
        'first_bloods_count': first_bloods_count,
        'first_bloods_points': first_bloods_points,
        'last_submission': last_submission,
        'rank': rank,
        'category_stats': category_stats,
        'member_stats': member_stats,
        'team_achievements': team_achievements,
        'can_view_invite_code': can_view_invite_code,
    }
    
    return render(request, 'teams/detail.html', context)

def team_join(request):
    """Vista para unirse a un equipo con código de invitación"""
    if request.method == 'POST':
        invite_code = request.POST.get('invite_code', '').strip().upper()
        
        if not invite_code:
            messages.error(request, 'Por favor ingresa un código de invitación.')
            return redirect('teams:join')
        
        try:
            team = Team.objects.get(invite_code=invite_code)
            
            # Verificar si el usuario ya está en un equipo
            if request.user.teams.exists():
                messages.error(request, 'Ya perteneces a un equipo. Debes salir primero.')
                return redirect('teams:join')
            
            # Agregar al usuario al equipo
            team.members.add(request.user)
            messages.success(request, f'¡Te has unido exitosamente al equipo "{team.name}"!')
            return redirect('teams:team_detail', team_id=team.id)
            
        except Team.DoesNotExist:
            messages.error(request, 'Código de invitación inválido.')
            return redirect('teams:join')
    
    return render(request, 'teams/join.html')

def team_leave(request, team_id):
    """Vista para salir de un equipo"""
    team = get_object_or_404(Team, id=team_id)
    
    if request.user not in team.members.all():
        messages.error(request, 'No perteneces a este equipo.')
        return redirect('teams:list')
    
    team.members.remove(request.user)
    messages.success(request, f'Has salido del equipo "{team.name}".')
    return redirect('teams:list')
