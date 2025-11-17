"""
Serializers para la API REST de ArenaCTF
Compatible con el formato de CTFd
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from challenges.models import Challenge, Category, Submission, FirstBlood
from teams.models import Team
from scoreboard.models import CTFConfig, Achievement

User = get_user_model()


# ==================== USER SERIALIZERS ====================

class UserListSerializer(serializers.ModelSerializer):
    """Serializer para listar usuarios (datos públicos)"""
    team_id = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'date_joined', 
            'team_id', 'is_staff'
        ]
        read_only_fields = ['id', 'date_joined']
    
    def get_team_id(self, obj):
        team = obj.teams.first()
        return str(team.id) if team else None


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para un usuario específico"""
    team_id = serializers.SerializerMethodField()
    team_name = serializers.SerializerMethodField()
    solves = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'date_joined', 'team_id', 'team_name', 'is_staff',
            'solves'
        ]
        read_only_fields = ['id', 'date_joined']
    
    def get_team_id(self, obj):
        team = obj.teams.first()
        return str(team.id) if team else None
    
    def get_team_name(self, obj):
        team = obj.teams.first()
        return team.name if team else None
    
    def get_solves(self, obj):
        team = obj.teams.first()
        if not team:
            return 0
        return Submission.objects.filter(
            team=team, 
            submitted_by=obj, 
            is_correct=True
        ).values('challenge').distinct().count()


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuarios"""
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


# ==================== TEAM SERIALIZERS ====================

class TeamListSerializer(serializers.ModelSerializer):
    """Serializer para listar equipos"""
    member_count = serializers.SerializerMethodField()
    solves = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'total_score', 'created_at', 
            'color', 'member_count', 'solves'
        ]
        read_only_fields = ['id', 'created_at', 'total_score']
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_solves(self, obj):
        return obj.get_solved_challenges_count()


class TeamDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para un equipo específico"""
    members = UserListSerializer(many=True, read_only=True)
    solves = serializers.SerializerMethodField()
    first_bloods = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'total_score', 'created_at', 'color',
            'avatar', 'members', 'solves', 'first_bloods', 'invite_code'
        ]
        read_only_fields = ['id', 'created_at', 'total_score', 'invite_code']
    
    def get_solves(self, obj):
        return obj.get_solved_challenges_count()
    
    def get_first_bloods(self, obj):
        return obj.get_first_bloods_count()


class TeamCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear equipos"""
    class Meta:
        model = Team
        fields = ['id', 'name', 'color']
        read_only_fields = ['id']


# ==================== CATEGORY SERIALIZERS ====================

class CategorySerializer(serializers.ModelSerializer):
    """Serializer para categorías"""
    challenge_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'color', 'challenge_count']
        read_only_fields = ['id']
    
    def get_challenge_count(self, obj):
        return obj.challenges.filter(is_active=True).count()


# ==================== CHALLENGE SERIALIZERS ====================

class ChallengeListSerializer(serializers.ModelSerializer):
    """Serializer para listar challenges"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    solves = serializers.SerializerMethodField()
    solved_by_me = serializers.SerializerMethodField()
    
    class Meta:
        model = Challenge
        fields = [
            'id', 'title', 'category', 'category_name', 'points', 
            'is_active', 'solves', 'solved_by_me', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_solves(self, obj):
        return obj.get_solve_count()
    
    def get_solved_by_me(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        team = request.user.teams.first()
        if not team:
            return False
        
        return Submission.objects.filter(
            team=team,
            challenge=obj,
            is_correct=True
        ).exists()


class ChallengeDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para un challenge específico"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    solves = serializers.SerializerMethodField()
    solved_by_me = serializers.SerializerMethodField()
    first_blood = serializers.SerializerMethodField()
    
    class Meta:
        model = Challenge
        fields = [
            'id', 'title', 'description', 'category', 'category_name',
            'category_icon', 'points', 'files', 'hints', 'is_active',
            'created_at', 'solves', 'solved_by_me', 'first_blood'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_solves(self, obj):
        return obj.get_solve_count()
    
    def get_solved_by_me(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        team = request.user.teams.first()
        if not team:
            return False
        
        return Submission.objects.filter(
            team=team,
            challenge=obj,
            is_correct=True
        ).exists()
    
    def get_first_blood(self, obj):
        try:
            fb = obj.first_blood
            return {
                'team_id': str(fb.team.id),
                'team_name': fb.team.name,
                'achieved_at': fb.achieved_at,
                'user': fb.achieved_by.username if fb.achieved_by else None
            }
        except FirstBlood.DoesNotExist:
            return None


class ChallengeCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear challenges (solo admins)"""
    class Meta:
        model = Challenge
        fields = [
            'id', 'title', 'description', 'category', 'points',
            'flag', 'files', 'hints', 'is_active'
        ]
        read_only_fields = ['id']


# ==================== SUBMISSION SERIALIZERS ====================

class SubmissionListSerializer(serializers.ModelSerializer):
    """Serializer para listar submissions"""
    team_name = serializers.CharField(source='team.name', read_only=True)
    challenge_title = serializers.CharField(source='challenge.title', read_only=True)
    user_name = serializers.CharField(source='submitted_by.username', read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'team', 'team_name', 'challenge', 'challenge_title',
            'is_correct', 'submitted_at', 'submitted_by', 'user_name'
        ]
        read_only_fields = ['id', 'submitted_at']


class SubmissionDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para una submission"""
    team_name = serializers.CharField(source='team.name', read_only=True)
    challenge_title = serializers.CharField(source='challenge.title', read_only=True)
    user_name = serializers.CharField(source='submitted_by.username', read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'team', 'team_name', 'challenge', 'challenge_title',
            'flag_submitted', 'is_correct', 'submitted_at',
            'submitted_by', 'user_name'
        ]
        read_only_fields = ['id', 'submitted_at', 'is_correct']


class SubmissionCreateSerializer(serializers.Serializer):
    """Serializer para enviar flags (intentar resolver challenges)"""
    challenge_id = serializers.UUIDField(required=True)
    flag = serializers.CharField(required=True, max_length=200)
    
    def validate(self, data):
        """Validar que el challenge existe y está activo"""
        try:
            challenge = Challenge.objects.get(id=data['challenge_id'], is_active=True)
            data['challenge'] = challenge
        except Challenge.DoesNotExist:
            raise serializers.ValidationError("Challenge no encontrado o inactivo")
        
        return data


# ==================== FIRST BLOOD SERIALIZERS ====================

class FirstBloodSerializer(serializers.ModelSerializer):
    """Serializer para first bloods"""
    team_name = serializers.CharField(source='team.name', read_only=True)
    challenge_title = serializers.CharField(source='challenge.title', read_only=True)
    user_name = serializers.CharField(source='achieved_by.username', read_only=True)
    
    class Meta:
        model = FirstBlood
        fields = [
            'id', 'team', 'team_name', 'challenge', 'challenge_title',
            'achieved_at', 'bonus_points', 'achieved_by', 'user_name'
        ]
        read_only_fields = ['id', 'achieved_at']


# ==================== CONFIG SERIALIZERS ====================

class CTFConfigSerializer(serializers.ModelSerializer):
    """Serializer para la configuración del CTF"""
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = CTFConfig
        fields = [
            'id', 'name', 'start_time', 'end_time', 'is_active',
            'first_blood_points', 'timezone', 'logo', 'status'
        ]
        read_only_fields = ['id']
    
    def get_status(self, obj):
        """Retorna el estado actual del CTF"""
        from django.utils import timezone
        now = timezone.now()
        
        if not obj.is_active:
            return 'inactive'
        
        if obj.start_time and now < obj.start_time:
            return 'pending'
        
        if obj.end_time and now > obj.end_time:
            return 'finished'
        
        return 'active'


# ==================== ACHIEVEMENT SERIALIZERS ====================

class AchievementSerializer(serializers.ModelSerializer):
    """Serializer para logros"""
    team_name = serializers.CharField(source='team.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    info = serializers.SerializerMethodField()
    
    class Meta:
        model = Achievement
        fields = [
            'id', 'code', 'team', 'team_name', 'user', 'user_name',
            'category', 'earned_at', 'info'
        ]
        read_only_fields = ['id', 'earned_at']
    
    def get_info(self, obj):
        info = obj.get_info()
        if info:
            return {
                'name': info.name,
                'description': info.description,
                'icon': info.icon,
                'category': info.category
            }
        return None


# ==================== SCOREBOARD SERIALIZERS ====================

class ScoreboardSerializer(serializers.Serializer):
    """Serializer para el scoreboard"""
    position = serializers.IntegerField()
    team_id = serializers.UUIDField()
    team_name = serializers.CharField()
    score = serializers.IntegerField()
    solves = serializers.IntegerField()
    first_bloods = serializers.IntegerField()
    last_solve_time = serializers.DateTimeField(allow_null=True)


class TeamSolvesSerializer(serializers.Serializer):
    """Serializer para los solves de un equipo"""
    challenge_id = serializers.UUIDField()
    challenge_title = serializers.CharField()
    challenge_category = serializers.CharField()
    points = serializers.IntegerField()
    solved_at = serializers.DateTimeField()
    solved_by = serializers.CharField()
    is_first_blood = serializers.BooleanField()


# ==================== STATISTICS SERIALIZERS ====================

class StatisticsSerializer(serializers.Serializer):
    """Serializer para estadísticas generales"""
    total_teams = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_challenges = serializers.IntegerField()
    total_submissions = serializers.IntegerField()
    correct_submissions = serializers.IntegerField()
    challenges_by_category = serializers.DictField()
    top_teams = ScoreboardSerializer(many=True)
