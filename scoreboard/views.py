from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db import models
from datetime import timedelta
import json
import pytz
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from teams.models import Team
from challenges.models import Challenge, Submission, FirstBlood
from .models import CTFConfig, Achievement
from .achievements import ACHIEVEMENTS

@login_required
def dashboard(request):
    """Vista principal del dashboard (requiere login)"""
    from django.db.models import Count
    import json
    
    teams = Team.objects.all().annotate(
        solved_count=Count('submissions', filter=models.Q(submissions__is_correct=True), distinct=True)
    ).order_by('-total_score', 'name')
    
    recent_submissions = Submission.objects.filter(is_correct=True).select_related('team', 'challenge').order_by('-submitted_at')[:10]
    first_bloods = FirstBlood.objects.all().select_related('team', 'challenge').order_by('-achieved_at')[:5]
    
    # Calcular estadísticas adicionales
    total_solves = Submission.objects.filter(is_correct=True).count()
    
    # Actividad en las últimas 24 horas
    last_24h = timezone.now() - timedelta(hours=24)
    recent_count = Submission.objects.filter(is_correct=True, submitted_at__gte=last_24h).count()
    
    # Preparar datos del timeline
    timeline_data = []
    config = CTFConfig.get_config()
    chile_tz = pytz.timezone('America/Santiago')
    
    for team in teams:
        team_submissions = Submission.objects.filter(
            team=team,
            is_correct=True
        ).order_by('submitted_at')
        
        cumulative_score = 0
        for submission in team_submissions:
            cumulative_score += submission.challenge.points
            
            # Agregar bonus de first blood si corresponde
            first_blood = FirstBlood.objects.filter(
                challenge=submission.challenge,
                team=team
            ).first()
            
            if first_blood:
                cumulative_score += first_blood.bonus_points
            
            timeline_data.append({
                'team': team.name,
                'time': submission.submitted_at.astimezone(chile_tz).isoformat(),
                'score': cumulative_score
            })
    
    context = {
        'teams': teams,
        'recent_submissions': recent_submissions,
        'first_bloods': first_bloods,
        'total_solves': total_solves,
        'recent_count': recent_count,
        'timeline_data': json.dumps(timeline_data),
        'last_update': timezone.now().astimezone(chile_tz).strftime('%d/%m/%Y %H:%M:%S'),
    }
    
    return render(request, 'scoreboard/dashboard.html', context)

def is_staff_or_moderator(user):
    """Verifica si el usuario es staff o moderador"""
    return user.is_staff or user.is_superuser

@user_passes_test(is_staff_or_moderator)
def public_display(request):
    """Vista pública para pantalla grande (solo admin/moderadores)"""
    teams = Team.objects.all().order_by('-total_score', 'name')
    recent_submissions = Submission.objects.filter(is_correct=True).select_related('team', 'challenge').order_by('-submitted_at')[:10]
    first_bloods = FirstBlood.objects.all().select_related('team', 'challenge').order_by('-achieved_at')[:10]
    
    # Generar datos del timeline
    timeline_list = []
    for team in teams:
        team_submissions = Submission.objects.filter(
            team=team,
            is_correct=True
        ).select_related('challenge').order_by('submitted_at')
        
        team_first_bloods = FirstBlood.objects.filter(
            team=team
        ).order_by('achieved_at')
        
        cumulative_score = 0
        for sub in team_submissions:
            cumulative_score += sub.challenge.points
            timeline_list.append({
                'team': team.name,
                'time': sub.submitted_at.isoformat(),
                'score': cumulative_score
            })
        
        for fb in team_first_bloods:
            cumulative_score += fb.bonus_points
            timeline_list.append({
                'team': team.name,
                'time': fb.achieved_at.isoformat(),
                'score': cumulative_score
            })
    
    # Ordenar por tiempo
    timeline_list.sort(key=lambda x: x['time'])
    
    context = {
        'teams': teams,
        'recent_submissions': recent_submissions,
        'first_bloods': first_bloods,
        'timeline_data': json.dumps(timeline_list),
    }
    
    return render(request, 'scoreboard/public_display.html', context)

def get_scoreboard_data(request):
    """API endpoint para obtener datos del scoreboard"""
    teams = Team.objects.all().order_by('-total_score', 'name')
    
    scoreboard_data = []
    for idx, team in enumerate(teams, 1):
        solved_challenges = Submission.objects.filter(
            team=team,
            is_correct=True
        ).count()
        
        first_bloods_count = FirstBlood.objects.filter(team=team).count()
        
        scoreboard_data.append({
            'rank': idx,
            'name': team.name,
            'score': team.total_score,
            'color': team.color,
            'solved': solved_challenges,
            'first_bloods': first_bloods_count,
        })
    
    return JsonResponse({'scoreboard': scoreboard_data})

@user_passes_test(is_staff_or_moderator)
def get_display_data(request):
    """API endpoint para datos del public display"""
    teams = Team.objects.all().order_by('-total_score', 'name')
    recent_submissions = Submission.objects.filter(is_correct=True).select_related('team', 'challenge').order_by('-submitted_at')[:10]
    first_bloods = FirstBlood.objects.all().select_related('team', 'challenge').order_by('-achieved_at')[:10]
    
    # Obtener configuración del CTF
    ctf_config = CTFConfig.get_config()
    start_time = ctf_config.start_time if ctf_config.start_time else timezone.now()
    
    teams_data = []
    timeline_data = {}
    
    for idx, team in enumerate(teams, 1):
        solved = Submission.objects.filter(team=team, is_correct=True).count()
        fb_count = FirstBlood.objects.filter(team=team).count()
        
        teams_data.append({
            'rank': idx,
            'name': team.name,
            'score': team.total_score,
            'color': team.color,
            'solved': solved,
            'first_bloods': fb_count,
        })
        
        # Obtener progreso del equipo para el timeline
        team_submissions = Submission.objects.filter(
            team=team, 
            is_correct=True
        ).order_by('submitted_at')
        
        team_first_bloods = FirstBlood.objects.filter(team=team).order_by('achieved_at')
        
        # Combinar submissions y first bloods en una lista ordenada por tiempo
        events = []
        
        # Convertir a zona horaria de Santiago
        chile_tz = pytz.timezone('America/Santiago')
        
        for sub in team_submissions:
            events.append({
                'time': sub.submitted_at.astimezone(chile_tz),
                'points': sub.challenge.points,
                'type': 'submission'
            })
        
        for fb in team_first_bloods:
            events.append({
                'time': fb.achieved_at.astimezone(chile_tz),
                'points': fb.bonus_points,
                'type': 'first_blood'
            })
        
        # Ordenar eventos por tiempo
        events.sort(key=lambda x: x['time'])
        
        # Crear progresión solo en minutos con actividad
        score_progression = []
        
        # Convertir a zona horaria de Santiago
        chile_tz = pytz.timezone('America/Santiago')
        start_time_chile = start_time.astimezone(chile_tz)
        
        # Agregar punto inicial (tiempo de inicio con puntaje 0)
        score_progression.append({
            'time': start_time_chile.isoformat(),
            'label': start_time_chile.strftime('%d/%m %H:%M'),
            'score': 0,
        })
        
        cumulative_score = 0
        last_minute = None
        
        # Solo agregar puntos cuando hay eventos
        for event in events:
            cumulative_score += event['points']
            event_time = event['time'].replace(second=0, microsecond=0)
            
            # Evitar duplicar el mismo minuto
            if event_time != last_minute:
                score_progression.append({
                    'time': event_time.isoformat(),
                    'label': event_time.strftime('%d/%m %H:%M'),
                    'score': cumulative_score,
                })
                last_minute = event_time
            else:
                # Si hay múltiples eventos en el mismo minuto, actualizar el puntaje del último punto
                score_progression[-1]['score'] = cumulative_score
        
        timeline_data[team.name] = {
            'color': team.color,
            'data': score_progression,
        }
    
    submissions_data = []
    for sub in recent_submissions:
        submissions_data.append({
            'team_name': sub.team.name,
            'team_color': sub.team.color,
            'user_name': sub.submitted_by.username if sub.submitted_by else 'Unknown',
            'challenge': sub.challenge.title,
            'points': sub.challenge.points,
            'time': sub.submitted_at.strftime('%H:%M:%S'),
        })
    
    first_bloods_data = []
    for fb in first_bloods:
        first_bloods_data.append({
            'team_name': fb.team.name,
            'team_color': fb.team.color,
            'user_name': fb.achieved_by.username if fb.achieved_by else 'Unknown',
            'challenge': fb.challenge.title,
            'points': fb.challenge.points,
            'time': fb.achieved_at.strftime('%H:%M:%S'),
        })
    
    return JsonResponse({
        'teams': teams_data,
        'recent_submissions': submissions_data,
        'first_bloods': first_bloods_data,
        'timeline': timeline_data,
    })

def broadcast_display_update(event_type=None, event_data=None):
    """Envía actualización de datos del display por WebSocket"""
    teams = Team.objects.all().order_by('-total_score', 'name')
    recent_submissions = Submission.objects.filter(is_correct=True).select_related('team', 'challenge').order_by('-submitted_at')[:10]
    first_bloods = FirstBlood.objects.all().select_related('team', 'challenge').order_by('-achieved_at')[:10]
    
    # Obtener configuración del CTF
    ctf_config = CTFConfig.get_config()
    start_time = ctf_config.start_time if ctf_config.start_time else timezone.now()
    
    teams_data = []
    timeline_data = {}
    
    for idx, team in enumerate(teams, 1):
        solved = Submission.objects.filter(team=team, is_correct=True).count()
        fb_count = FirstBlood.objects.filter(team=team).count()
        
        teams_data.append({
            'id': str(team.id),
            'rank': idx,
            'name': team.name,
            'score': team.total_score,
            'color': team.color,
            'solved': solved,
            'first_bloods': fb_count,
        })
        
        # Obtener progreso del equipo para el timeline
        team_submissions = Submission.objects.filter(
            team=team, 
            is_correct=True
        ).order_by('submitted_at')
        
        team_first_bloods = FirstBlood.objects.filter(team=team).order_by('achieved_at')
        
        # Combinar submissions y first bloods en una lista ordenada por tiempo
        events = []
        
        # Convertir a zona horaria de Santiago
        chile_tz = pytz.timezone('America/Santiago')
        
        for sub in team_submissions:
            events.append({
                'time': sub.submitted_at.astimezone(chile_tz),
                'points': sub.challenge.points,
                'type': 'submission'
            })
        
        for fb in team_first_bloods:
            events.append({
                'time': fb.achieved_at.astimezone(chile_tz),
                'points': fb.bonus_points,
                'type': 'first_blood'
            })
        
        # Ordenar eventos por tiempo
        events.sort(key=lambda x: x['time'])
        
        # Crear progresión solo en minutos con actividad
        score_progression = []
        
        # Convertir a zona horaria de Santiago
        chile_tz = pytz.timezone('America/Santiago')
        start_time_chile = start_time.astimezone(chile_tz)
        
        # Agregar punto inicial (tiempo de inicio con puntaje 0)
        score_progression.append({
            'time': start_time_chile.isoformat(),
            'label': start_time_chile.strftime('%d/%m %H:%M'),
            'score': 0,
        })
        
        cumulative_score = 0
        last_minute = None
        
        # Solo agregar puntos cuando hay eventos
        for event in events:
            cumulative_score += event['points']
            event_time = event['time'].replace(second=0, microsecond=0)
            
            # Evitar duplicar el mismo minuto
            if event_time != last_minute:
                score_progression.append({
                    'time': event_time.isoformat(),
                    'label': event_time.strftime('%d/%m %H:%M'),
                    'score': cumulative_score,
                })
                last_minute = event_time
            else:
                # Si hay múltiples eventos en el mismo minuto, actualizar el puntaje del último punto
                score_progression[-1]['score'] = cumulative_score
        
        timeline_data[team.name] = {
            'color': team.color,
            'data': score_progression,
        }
    
    # Convertir timeline_data a lista para el frontend
    timeline_list = []
    for team_name, team_timeline in timeline_data.items():
        for point in team_timeline['data']:
            timeline_list.append({
                'team': team_name,
                'time': point['time'],
                'score': point['score']
            })
    
    submissions_data = []
    chile_tz = pytz.timezone('America/Santiago')
    for sub in recent_submissions:
        time_diff = timezone.now() - sub.submitted_at
        if time_diff.seconds < 60:
            time_ago = 'justo ahora'
        elif time_diff.seconds < 3600:
            minutes = time_diff.seconds // 60
            time_ago = f'hace {minutes}m'
        elif time_diff.days == 0:
            hours = time_diff.seconds // 3600
            time_ago = f'hace {hours}h'
        else:
            time_ago = f'hace {time_diff.days}d'
            
        submissions_data.append({
            'team': sub.team.name,
            'team_color': sub.team.color,
            'user_name': sub.submitted_by.username if sub.submitted_by else 'Unknown',
            'challenge': sub.challenge.title,
            'points': sub.challenge.points,
            'time': sub.submitted_at.strftime('%H:%M:%S'),
            'time_ago': time_ago,
        })
    
    first_bloods_data = []
    for fb in first_bloods:
        first_bloods_data.append({
            'team': fb.team.name,
            'team_color': fb.team.color,
            'user_name': fb.achieved_by.username if fb.achieved_by else 'Unknown',
            'challenge': fb.challenge.title,
            'points': fb.challenge.points,
            'bonus_points': fb.bonus_points,
            'time': fb.achieved_at.strftime('%H:%M:%S'),
        })
    
    # Enviar por WebSocket
    channel_layer = get_channel_layer()
    message_data = {
        'type': 'display_data_update',
        'teams': teams_data,
        'recent_submissions': submissions_data,
        'first_bloods': first_bloods_data,
        'timeline': timeline_list,
    }
    
    # Agregar información del evento si existe
    if event_type and event_data:
        message_data['event_type'] = event_type
        message_data['event_data'] = event_data
    
    async_to_sync(channel_layer.group_send)(
        'scoreboard',
        message_data
    )

@login_required
def achievements_list(request):
    """Vista para mostrar todos los logros disponibles"""
    user_team = request.user.teams.first()
    
    # Obtener todos los logros del equipo (solo códigos que existen en ACHIEVEMENTS)
    team_earned_codes = []
    if user_team:
        db_team_codes = Achievement.objects.filter(
            team=user_team,
            category='team'
        ).values_list('code', flat=True)
        # Filtrar solo los que están definidos en ACHIEVEMENTS
        team_earned_codes = [code for code in db_team_codes if code in ACHIEVEMENTS]
    
    # Obtener logros individuales del usuario (solo códigos que existen en ACHIEVEMENTS)
    db_individual_codes = Achievement.objects.filter(
        user=request.user,
        category='individual'
    ).values_list('code', flat=True)
    # Filtrar solo los que están definidos en ACHIEVEMENTS
    individual_earned_codes = [code for code in db_individual_codes if code in ACHIEVEMENTS]
    
    # Preparar logros de equipo
    team_achievements = []
    for code, achievement_def in ACHIEVEMENTS.items():
        if achievement_def.category == 'team':
            earned_achievement = None
            if code in team_earned_codes and user_team:
                try:
                    earned_achievement = Achievement.objects.get(code=code, team=user_team)
                except Achievement.DoesNotExist:
                    pass
            
            team_achievements.append({
                'code': code,
                'name': achievement_def.name,
                'description': achievement_def.description,
                'icon': achievement_def.icon,
                'earned': code in team_earned_codes,
                'earned_at': earned_achievement.earned_at if earned_achievement else None,
            })
    
    # Preparar logros individuales
    individual_achievements = []
    for code, achievement_def in ACHIEVEMENTS.items():
        if achievement_def.category == 'individual':
            earned_achievement = None
            if code in individual_earned_codes:
                try:
                    earned_achievement = Achievement.objects.get(code=code, user=request.user)
                except Achievement.DoesNotExist:
                    pass
            
            individual_achievements.append({
                'code': code,
                'name': achievement_def.name,
                'description': achievement_def.description,
                'icon': achievement_def.icon,
                'earned': code in individual_earned_codes,
                'earned_at': earned_achievement.earned_at if earned_achievement else None,
            })
    
    # Estadísticas
    total_team = len(team_achievements)
    earned_team = len(team_earned_codes)
    total_individual = len(individual_achievements)
    earned_individual = len(individual_earned_codes)
    
    context = {
        'user_team': user_team,
        'team_achievements': team_achievements,
        'individual_achievements': individual_achievements,
        'total_team': total_team,
        'earned_team': earned_team,
        'total_individual': total_individual,
        'earned_individual': earned_individual,
    }
    
    return render(request, 'scoreboard/achievements.html', context)
