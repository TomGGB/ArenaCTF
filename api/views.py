"""
ViewSets para la API REST de ArenaCTF
Compatible con CTFd API
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Q, Max, Sum
from datetime import datetime

from challenges.models import Challenge, Category, Submission, FirstBlood
from teams.models import Team
from scoreboard.models import CTFConfig, Achievement
from .serializers import *
from .permissions import (
    IsAdminOrReadOnly, IsOwnerOrAdmin, IsTeamMemberOrAdmin,
    IsCTFActive, HasTeam, CanSubmitFlag
)

User = get_user_model()


# ==================== USER VIEWSETS ====================

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios
    
    list: Listar todos los usuarios (público)
    retrieve: Obtener detalles de un usuario específico
    create: Crear nuevo usuario (público para registro)
    update: Actualizar usuario (solo el mismo usuario o admin)
    destroy: Eliminar usuario (solo admin)
    me: Obtener información del usuario autenticado
    """
    queryset = User.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined']
    ordering = ['username']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['retrieve', 'me']:
            return UserDetailSerializer
        return UserListSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]
        elif self.action == 'me':
            return [IsAuthenticated()]
        return [AllowAny()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener información del usuario autenticado"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def solves(self, request, pk=None):
        """Obtener los solves de un usuario"""
        user = self.get_object()
        team = user.teams.first()
        
        if not team:
            return Response({'solves': []})
        
        submissions = Submission.objects.filter(
            team=team,
            submitted_by=user,
            is_correct=True
        ).select_related('challenge', 'challenge__category').order_by('-submitted_at')
        
        solves = []
        for sub in submissions:
            is_first_blood = FirstBlood.objects.filter(
                challenge=sub.challenge,
                achieved_by=user
            ).exists()
            
            solves.append({
                'challenge_id': str(sub.challenge.id),
                'challenge_title': sub.challenge.title,
                'challenge_category': sub.challenge.category.name,
                'points': sub.challenge.points,
                'solved_at': sub.submitted_at,
                'is_first_blood': is_first_blood
            })
        
        return Response({'solves': solves})
    
    @action(detail=True, methods=['get'])
    def fails(self, request, pk=None):
        """Obtener los intentos fallidos de un usuario"""
        user = self.get_object()
        team = user.teams.first()
        
        if not team:
            return Response({'fails': []})
        
        # Solo mostrar a admins o al mismo usuario
        if not (request.user.is_staff or request.user == user):
            return Response(
                {'error': 'No tienes permiso para ver esta información'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        fails = Submission.objects.filter(
            team=team,
            submitted_by=user,
            is_correct=False
        ).select_related('challenge').order_by('-submitted_at')[:50]
        
        serializer = SubmissionListSerializer(fails, many=True)
        return Response({'fails': serializer.data})


# ==================== TEAM VIEWSETS ====================

class TeamViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar equipos
    
    list: Listar todos los equipos
    retrieve: Obtener detalles de un equipo específico
    create: Crear nuevo equipo
    update: Actualizar equipo (solo miembros o admin)
    destroy: Eliminar equipo (solo admin)
    join: Unirse a un equipo con código de invitación
    leave: Abandonar un equipo
    """
    queryset = Team.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'total_score', 'created_at']
    ordering = ['-total_score']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TeamCreateSerializer
        elif self.action == 'retrieve':
            return TeamDetailSerializer
        return TeamListSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update']:
            return [IsTeamMemberOrAdmin()]
        elif self.action == 'destroy':
            return [IsAdminUser()]
        elif self.action in ['join', 'leave']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def perform_create(self, serializer):
        """Al crear un equipo, agregar al usuario como miembro"""
        team = serializer.save()
        team.members.add(self.request.user)
    
    @action(detail=False, methods=['post'])
    def join(self, request):
        """Unirse a un equipo usando código de invitación"""
        invite_code = request.data.get('invite_code')
        
        if not invite_code:
            return Response(
                {'error': 'Se requiere un código de invitación'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            team = Team.objects.get(invite_code=invite_code)
        except Team.DoesNotExist:
            return Response(
                {'error': 'Código de invitación inválido'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar si ya pertenece a un equipo
        if request.user.teams.exists():
            return Response(
                {'error': 'Ya perteneces a un equipo. Debes salir primero.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        team.members.add(request.user)
        serializer = TeamDetailSerializer(team)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Abandonar un equipo"""
        team = self.get_object()
        
        if request.user not in team.members.all():
            return Response(
                {'error': 'No perteneces a este equipo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        team.members.remove(request.user)
        return Response({'message': 'Has abandonado el equipo exitosamente'})
    
    @action(detail=True, methods=['get'])
    def solves(self, request, pk=None):
        """Obtener los solves de un equipo"""
        team = self.get_object()
        
        submissions = Submission.objects.filter(
            team=team,
            is_correct=True
        ).select_related(
            'challenge', 'challenge__category', 'submitted_by'
        ).order_by('-submitted_at')
        
        solves = []
        for sub in submissions:
            is_first_blood = FirstBlood.objects.filter(
                challenge=sub.challenge,
                team=team
            ).exists()
            
            solves.append({
                'challenge_id': str(sub.challenge.id),
                'challenge_title': sub.challenge.title,
                'challenge_category': sub.challenge.category.name,
                'points': sub.challenge.points,
                'solved_at': sub.submitted_at,
                'solved_by': sub.submitted_by.username if sub.submitted_by else 'Unknown',
                'is_first_blood': is_first_blood
            })
        
        return Response({'solves': solves})
    
    @action(detail=True, methods=['get'])
    def fails(self, request, pk=None):
        """Obtener los intentos fallidos de un equipo (solo miembros o admin)"""
        team = self.get_object()
        
        # Solo mostrar a admins o miembros del equipo
        if not (request.user.is_staff or request.user in team.members.all()):
            return Response(
                {'error': 'No tienes permiso para ver esta información'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        fails = Submission.objects.filter(
            team=team,
            is_correct=False
        ).select_related('challenge', 'submitted_by').order_by('-submitted_at')[:100]
        
        serializer = SubmissionListSerializer(fails, many=True)
        return Response({'fails': serializer.data})
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Obtener los miembros de un equipo"""
        team = self.get_object()
        members = team.members.all()
        serializer = UserListSerializer(members, many=True)
        return Response({'members': serializer.data})


# ==================== CATEGORY VIEWSETS ====================

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar categorías de challenges
    
    list: Listar todas las categorías
    retrieve: Obtener detalles de una categoría específica
    create: Crear nueva categoría (solo admin)
    update: Actualizar categoría (solo admin)
    destroy: Eliminar categoría (solo admin)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def challenges(self, request, pk=None):
        """Obtener los challenges de una categoría"""
        category = self.get_object()
        challenges = category.challenges.filter(is_active=True)
        serializer = ChallengeListSerializer(
            challenges, 
            many=True, 
            context={'request': request}
        )
        return Response({'challenges': serializer.data})


# ==================== CHALLENGE VIEWSETS ====================

class ChallengeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar challenges
    
    list: Listar todos los challenges activos
    retrieve: Obtener detalles de un challenge específico
    create: Crear nuevo challenge (solo admin)
    update: Actualizar challenge (solo admin)
    destroy: Eliminar challenge (solo admin)
    attempt: Intentar resolver un challenge enviando una flag
    solves: Ver quién ha resuelto el challenge
    """
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'points']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'points', 'created_at']
    ordering = ['category', 'points']
    
    def get_queryset(self):
        """Solo mostrar challenges activos a no-admins y solo si el CTF ha iniciado"""
        if self.request.user.is_staff:
            return Challenge.objects.all()
        
        # Para usuarios normales, solo mostrar challenges si el CTF ha comenzado
        from scoreboard.models import CTFConfig
        config = CTFConfig.get_config()
        
        if not config.has_started():
            return Challenge.objects.none()
        
        return Challenge.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ChallengeCreateSerializer
        elif self.action == 'retrieve':
            return ChallengeDetailSerializer
        elif self.action == 'attempt':
            return SubmissionCreateSerializer
        return ChallengeListSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        elif self.action == 'attempt':
            return [CanSubmitFlag()]
        return [AllowAny()]
    
    @action(detail=False, methods=['post'])
    def attempt(self, request):
        """
        Intentar resolver un challenge enviando una flag
        
        Body: {
            "challenge_id": "uuid",
            "flag": "flag{...}"
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        challenge = serializer.validated_data['challenge']
        flag = serializer.validated_data['flag']
        team = request.user.teams.first()
        
        if not team:
            return Response(
                {'error': 'Debes pertenecer a un equipo para enviar flags'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si ya fue resuelto por el equipo
        already_solved = Submission.objects.filter(
            team=team,
            challenge=challenge,
            is_correct=True
        ).exists()
        
        if already_solved:
            return Response(
                {
                    'success': False,
                    'message': 'Ya has resuelto este challenge',
                    'is_correct': False
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar la flag
        is_correct = flag.strip() == challenge.flag.strip()
        
        # Crear submission
        submission = Submission.objects.create(
            team=team,
            challenge=challenge,
            flag_submitted=flag,
            is_correct=is_correct,
            submitted_by=request.user
        )
        
        response_data = {
            'success': is_correct,
            'is_correct': is_correct,
            'submission_id': str(submission.id)
        }
        
        if is_correct:
            # Actualizar score del equipo
            team.update_score()
            
            # Verificar first blood
            is_first_blood = not FirstBlood.objects.filter(challenge=challenge).exists()
            
            if is_first_blood:
                config = CTFConfig.get_config()
                FirstBlood.objects.create(
                    team=team,
                    challenge=challenge,
                    bonus_points=config.first_blood_points,
                    achieved_by=request.user
                )
                response_data['first_blood'] = True
                response_data['bonus_points'] = config.first_blood_points
            
            response_data['message'] = '¡Correcto! Has ganado {} puntos'.format(challenge.points)
            response_data['points_earned'] = challenge.points
            response_data['team_score'] = team.total_score
            
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data['message'] = 'Flag incorrecta. Inténtalo de nuevo.'
            return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def solves(self, request, pk=None):
        """Ver quién ha resuelto el challenge"""
        challenge = self.get_object()
        
        submissions = Submission.objects.filter(
            challenge=challenge,
            is_correct=True
        ).select_related('team', 'submitted_by').order_by('submitted_at')
        
        solves = []
        for sub in submissions:
            is_first_blood = FirstBlood.objects.filter(
                challenge=challenge,
                team=sub.team
            ).exists()
            
            solves.append({
                'team_id': str(sub.team.id),
                'team_name': sub.team.name,
                'user': sub.submitted_by.username if sub.submitted_by else 'Unknown',
                'solved_at': sub.submitted_at,
                'is_first_blood': is_first_blood
            })
        
        return Response({
            'challenge_id': str(challenge.id),
            'challenge_title': challenge.title,
            'total_solves': len(solves),
            'solves': solves
        })
    
    @action(detail=True, methods=['get'])
    def files(self, request, pk=None):
        """Obtener archivos del challenge"""
        challenge = self.get_object()
        
        if challenge.files:
            return Response({
                'files': [
                    {
                        'name': challenge.files.name.split('/')[-1],
                        'url': request.build_absolute_uri(challenge.files.url)
                    }
                ]
            })
        
        return Response({'files': []})


# ==================== SUBMISSION VIEWSETS ====================

class SubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ver submissions (solo lectura desde API, use /challenges/attempt para enviar)
    
    list: Listar submissions (filtradas según permisos)
    retrieve: Obtener detalles de una submission específica
    """
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['team', 'challenge', 'is_correct']
    ordering_fields = ['submitted_at']
    ordering = ['-submitted_at']
    
    def get_queryset(self):
        """Filtrar submissions según permisos"""
        user = self.request.user
        
        if user.is_staff:
            # Admins ven todo
            return Submission.objects.all()
        elif user.is_authenticated:
            # Usuarios autenticados solo ven las de su equipo
            team = user.teams.first()
            if team:
                return Submission.objects.filter(team=team)
        
        # No autenticados no ven nada
        return Submission.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubmissionDetailSerializer
        return SubmissionListSerializer


# ==================== FIRST BLOOD VIEWSETS ====================

class FirstBloodViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ver first bloods (solo lectura)
    
    list: Listar todos los first bloods
    retrieve: Obtener detalles de un first blood específico
    """
    queryset = FirstBlood.objects.all().select_related('team', 'challenge', 'achieved_by')
    serializer_class = FirstBloodSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['team', 'challenge']
    ordering_fields = ['achieved_at']
    ordering = ['-achieved_at']


# ==================== CONFIG VIEWSETS ====================

class CTFConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la configuración del CTF
    
    list: Ver configuración actual
    update: Actualizar configuración (solo admin)
    """
    queryset = CTFConfig.objects.all()
    serializer_class = CTFConfigSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'create', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Obtener la configuración actual del CTF"""
        config = CTFConfig.get_config()
        serializer = self.get_serializer(config)
        return Response(serializer.data)


# ==================== SCOREBOARD VIEWSETS ====================

class ScoreboardViewSet(viewsets.ViewSet):
    """
    ViewSet para el scoreboard
    
    list: Obtener el scoreboard completo
    top: Obtener top N equipos
    """
    permission_classes = [AllowAny]
    
    def list(self, request):
        """Obtener el scoreboard completo ordenado por puntuación"""
        teams = Team.objects.annotate(
            solves_count=Count(
                'submissions',
                filter=Q(submissions__is_correct=True),
                distinct=True
            ),
            first_bloods_count=Count('first_bloods', distinct=True),
            last_solve=Max(
                'submissions__submitted_at',
                filter=Q(submissions__is_correct=True)
            )
        ).order_by('-total_score', 'last_solve')
        
        scoreboard = []
        for position, team in enumerate(teams, start=1):
            scoreboard.append({
                'position': position,
                'team_id': str(team.id),
                'team_name': team.name,
                'score': team.total_score,
                'solves': team.solves_count,
                'first_bloods': team.first_bloods_count,
                'last_solve_time': team.last_solve
            })
        
        return Response({'scoreboard': scoreboard})
    
    @action(detail=False, methods=['get'])
    def top(self, request):
        """Obtener top N equipos"""
        count = int(request.query_params.get('count', 10))
        
        teams = Team.objects.annotate(
            solves_count=Count(
                'submissions',
                filter=Q(submissions__is_correct=True),
                distinct=True
            ),
            first_bloods_count=Count('first_bloods', distinct=True),
            last_solve=Max(
                'submissions__submitted_at',
                filter=Q(submissions__is_correct=True)
            )
        ).order_by('-total_score', 'last_solve')[:count]
        
        top_teams = []
        for position, team in enumerate(teams, start=1):
            top_teams.append({
                'position': position,
                'team_id': str(team.id),
                'team_name': team.name,
                'score': team.total_score,
                'solves': team.solves_count,
                'first_bloods': team.first_bloods_count,
                'last_solve_time': team.last_solve
            })
        
        return Response({'top_teams': top_teams})


# ==================== STATISTICS VIEWSETS ====================

class StatisticsViewSet(viewsets.ViewSet):
    """
    ViewSet para estadísticas del CTF
    
    list: Estadísticas generales (alias de overview)
    overview: Estadísticas generales
    challenges: Estadísticas de challenges por categoría
    """
    permission_classes = [AllowAny]
    
    def list(self, request):
        """Estadísticas generales del CTF (mismo que overview)"""
        return self.overview(request)
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Estadísticas generales del CTF"""
        stats = {
            'total_teams': Team.objects.count(),
            'total_users': User.objects.count(),
            'total_challenges': Challenge.objects.filter(is_active=True).count(),
            'total_submissions': Submission.objects.count(),
            'correct_submissions': Submission.objects.filter(is_correct=True).count(),
            'total_first_bloods': FirstBlood.objects.count(),
        }
        
        # Challenges por categoría
        categories = Category.objects.annotate(
            challenge_count=Count('challenges', filter=Q(challenges__is_active=True))
        )
        
        stats['challenges_by_category'] = {
            cat.name: cat.challenge_count for cat in categories
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def challenges(self, request):
        """Estadísticas de challenges"""
        challenges = Challenge.objects.filter(is_active=True).annotate(
            solve_count=Count('submissions', filter=Q(submissions__is_correct=True))
        ).select_related('category')
        
        challenge_stats = []
        for challenge in challenges:
            challenge_stats.append({
                'id': str(challenge.id),
                'title': challenge.title,
                'category': challenge.category.name,
                'points': challenge.points,
                'solves': challenge.solve_count,
                'has_first_blood': FirstBlood.objects.filter(challenge=challenge).exists()
            })
        
        return Response({'challenges': challenge_stats})


# ==================== ACHIEVEMENT VIEWSETS ====================

class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ver logros
    
    list: Listar todos los logros
    retrieve: Obtener detalles de un logro específico
    """
    queryset = Achievement.objects.all().select_related('team', 'user')
    serializer_class = AchievementSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['team', 'user', 'category']
    ordering_fields = ['earned_at']
    ordering = ['-earned_at']
