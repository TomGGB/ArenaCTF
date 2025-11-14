from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db import models
from datetime import timedelta
import pytz
from teams.models import Team
from challenges.models import Challenge, Submission, FirstBlood
from .models import CTFConfig

@login_required
def dashboard(request):
    """Vista principal del dashboard (requiere login)"""
    from django.db.models import Count
    
    teams = Team.objects.all().annotate(
        solved_count=Count('submissions', filter=models.Q(submissions__is_correct=True), distinct=True)
    ).order_by('-total_score', 'name')[:10]
    recent_submissions = Submission.objects.filter(is_correct=True).select_related('team', 'challenge').order_by('-submitted_at')[:10]
    first_bloods = FirstBlood.objects.all().select_related('team', 'challenge').order_by('-achieved_at')[:5]
    
    context = {
        'teams': teams,
        'recent_submissions': recent_submissions,
        'first_bloods': first_bloods,
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
    
    context = {
        'teams': teams,
        'recent_submissions': recent_submissions,
        'first_bloods': first_bloods,
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
        
        # Crear progresión minuto a minuto desde el inicio hasta ahora
        score_progression = []
        current_time = timezone.now()
        
        # Convertir a zona horaria de Santiago
        chile_tz = pytz.timezone('America/Santiago')
        current_time_chile = current_time.astimezone(chile_tz)
        start_time_chile = start_time.astimezone(chile_tz)
        
        # Generar lista de todos los minutos desde el inicio hasta ahora
        time_cursor = start_time_chile.replace(second=0, microsecond=0)
        end_time_rounded = current_time_chile.replace(second=0, microsecond=0)
        
        cumulative_score = 0
        event_index = 0
        
        while time_cursor <= end_time_rounded:
            time_str = time_cursor.strftime('%H:%M')
            
            # Sumar puntos de todos los eventos que ocurrieron en este minuto
            while event_index < len(events) and events[event_index]['time'].replace(second=0, microsecond=0) <= time_cursor:
                cumulative_score += events[event_index]['points']
                event_index += 1
            
            score_progression.append({
                'time': time_str,
                'score': cumulative_score,
            })
            
            # Avanzar al siguiente minuto
            time_cursor += timedelta(minutes=1)
        
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
