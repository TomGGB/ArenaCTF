from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Challenge, Submission, FirstBlood, Category
from teams.models import Team
from scoreboard.models import CTFConfig, Achievement
from scoreboard.achievements import check_achievements
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@login_required
def challenge_list(request):
    """Vista para listar todos los challenges"""
    # Verificar que el usuario tenga un equipo (excepto staff/superusers)
    user_team = request.user.teams.first()
    
    if not user_team and not (request.user.is_staff or request.user.is_superuser):
        # Obtener todos los equipos para mostrar opciones
        teams = Team.objects.all()
        context = {
            'teams': teams,
            'user': request.user,
        }
        return render(request, 'challenges/no_team.html', context)
    
    categories = Category.objects.all()
    challenges = Challenge.objects.filter(is_active=True)
    
    # Si no hay challenges, mostrar pantalla apropiada
    if not challenges.exists():
        context = {
            'is_staff': request.user.is_staff or request.user.is_superuser,
        }
        return render(request, 'challenges/no_challenges.html', context)
    
    # Marcar challenges resueltos por el equipo (si tiene)
    solved_challenges = []
    if user_team:
        solved_challenges = Submission.objects.filter(
            team=user_team,
            is_correct=True
        ).values_list('challenge_id', flat=True)
    
    # Verificar si el CTF ha terminado
    ctf_config = CTFConfig.get_config()
    ctf_ended = ctf_config.end_time and timezone.now() > ctf_config.end_time
    
    context = {
        'categories': categories,
        'challenges': challenges,
        'solved_challenges': solved_challenges,
        'user_team': user_team,
        'ctf_ended': ctf_ended,
        'ctf_config': ctf_config,
    }
    
    return render(request, 'challenges/list.html', context)

@login_required
def challenge_detail(request, challenge_id):
    """Vista para ver detalles de un challenge"""
    # Verificar si el CTF ha terminado
    ctf_config = CTFConfig.get_config()
    if ctf_config.end_time and timezone.now() > ctf_config.end_time:
        messages.error(request, '⏰ El CTF ha finalizado. Los challenges están en modo solo lectura.')
        return redirect('challenges:list')
    
    # Verificar que el usuario tenga un equipo (excepto staff/superusers)
    user_team = request.user.teams.first()
    
    if not user_team and not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Debes unirte a un equipo primero'}, status=403)
    
    challenge = get_object_or_404(Challenge, id=challenge_id, is_active=True)
    
    # Verificar si el equipo ya resolvió este challenge
    solved = False
    if user_team:
        solved = Submission.objects.filter(
            team=user_team,
            challenge=challenge,
            is_correct=True
        ).exists()
    
    context = {
        'challenge': challenge,
        'user_team': user_team,
        'solved': solved,
        'solve_count': challenge.get_solve_count(),
    }
    
    return render(request, 'challenges/detail.html', context)

@login_required
def submit_flag(request, challenge_id):
    """Vista para enviar una flag"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    # Verificar si el CTF está activo y dentro del tiempo permitido
    ctf_config = CTFConfig.get_config()
    if ctf_config.end_time and timezone.now() > ctf_config.end_time:
        return JsonResponse({
            'error': '⏰ El CTF ha finalizado. Ya no se aceptan más submissions. El tiempo límite era: ' + ctf_config.end_time.strftime('%d/%m/%Y %H:%M:%S')
        }, status=403)
    
    challenge = get_object_or_404(Challenge, id=challenge_id, is_active=True)
    user_team = request.user.teams.first()
    
    if not user_team:
        return JsonResponse({'error': 'Debes pertenecer a un equipo'}, status=400)
    
    flag = request.POST.get('flag', '').strip()
    
    # Verificar si algún miembro del equipo ya resolvió este challenge
    already_solved = Submission.objects.filter(
        team=user_team,
        challenge=challenge,
        is_correct=True
    ).exists()
    
    if already_solved:
        # Obtener quién lo resolvió
        solver = Submission.objects.filter(
            team=user_team,
            challenge=challenge,
            is_correct=True
        ).first().submitted_by
        return JsonResponse({
            'error': f'Este challenge ya fue resuelto por {solver.username} de tu equipo'
        }, status=400)
    
    # Verificar si la flag es correcta
    is_correct = flag == challenge.flag
    
    # Crear submission
    submission = Submission.objects.create(
        team=user_team,
        challenge=challenge,
        flag_submitted=flag,
        is_correct=is_correct,
        submitted_by=request.user
    )
    
    if is_correct:
        # Verificar si es first blood
        is_first_blood = not FirstBlood.objects.filter(challenge=challenge).exists()
        
        if is_first_blood:
            # Obtener puntos configurados de first blood
            config = CTFConfig.get_config()
            first_blood = FirstBlood.objects.create(
                team=user_team,
                challenge=challenge,
                achieved_by=request.user,
                bonus_points=config.first_blood_points
            )
        
        # Actualizar puntaje del equipo (después de crear first blood)
        user_team.update_score()
        
        # Verificar logros del equipo y jugador
        team_achievements = check_achievements(user_team)
        individual_achievements = check_achievements(user_team, request.user)
        
        # Guardar nuevos logros (solo para notificaciones en display mostrar individuales)
        new_achievements = []
        
        # Guardar logros de equipo en DB pero no agregarlos a notificaciones del display
        for achievement_code in team_achievements:
            Achievement.objects.get_or_create(
                code=achievement_code,
                team=user_team,
                defaults={'category': 'team'}
            )
        
        # Solo agregar logros individuales a las notificaciones (incluyen info del equipo)
        for achievement_code in individual_achievements:
            achievement, created = Achievement.objects.get_or_create(
                code=achievement_code,
                user=request.user,
                defaults={'category': 'individual'}
            )
            if created:
                new_achievements.append({
                    'type': 'individual',
                    'code': achievement_code,
                    'name': achievement.get_info().name,
                    'icon': achievement.get_info().icon,
                    'user': request.user.username,
                    'team': user_team.name,
                    'color': user_team.color,
                })
        
        # Enviar actualización completa del display con información del evento
        from scoreboard.views import broadcast_display_update
        broadcast_display_update(
            event_type='flag_solved',
            event_data={
                'team': user_team.name,
                'challenge': challenge.title,
                'points': challenge.points,
                'color': user_team.color,
                'is_first_blood': is_first_blood,
                'new_achievements': new_achievements,
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': '¡Flag correcta! 🎉',
            'is_first_blood': is_first_blood,
            'points': challenge.points,
            'new_achievements': new_achievements,
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Flag incorrecta ❌'
        })
