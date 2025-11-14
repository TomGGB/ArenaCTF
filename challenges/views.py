from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Challenge, Submission, FirstBlood, Category
from teams.models import Team
from scoreboard.models import CTFConfig
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
    
    context = {
        'categories': categories,
        'challenges': challenges,
        'solved_challenges': solved_challenges,
        'user_team': user_team,
    }
    
    return render(request, 'challenges/list.html', context)

@login_required
def challenge_detail(request, challenge_id):
    """Vista para ver detalles de un challenge"""
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
        
        if is_first_blood:
            # Enviar notificación de first blood por WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'scoreboard',
                {
                    'type': 'first_blood_notification',
                    'team': user_team.name,
                    'challenge': challenge.title,
                    'color': user_team.color,
                }
            )
        
        # Enviar notificación de flag correcta por WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'scoreboard',
            {
                'type': 'flag_solved_notification',
                'team': user_team.name,
                'challenge': challenge.title,
                'points': challenge.points,
                'color': user_team.color,
                'is_first_blood': is_first_blood,
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': '¡Flag correcta! 🎉',
            'is_first_blood': is_first_blood,
            'points': challenge.points,
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Flag incorrecta ❌'
        })
