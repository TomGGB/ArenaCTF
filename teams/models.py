from django.db import models
from django.conf import settings
import uuid
import secrets
import string

class Team(models.Model):
    """Modelo para equipos participantes en el CTF"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre del equipo")
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='teams', verbose_name="Miembros")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    color = models.CharField(max_length=7, default="#FF0000", verbose_name="Color del equipo")
    avatar = models.ImageField(upload_to='team_avatars/', null=True, blank=True, verbose_name="Avatar")
    total_score = models.IntegerField(default=0, verbose_name="Puntuación total")
    invite_code = models.CharField(max_length=8, unique=True, blank=True, verbose_name="Código de invitación")
    
    def save(self, *args, **kwargs):
        """Generar código de invitación si no existe"""
        if not self.invite_code:
            self.invite_code = self.generate_invite_code()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_invite_code():
        """Generar un código de invitación aleatorio único"""
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            if not Team.objects.filter(invite_code=code).exists():
                return code
    
    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ['-total_score', 'name']
    
    def __str__(self):
        return self.name
    
    def get_solved_challenges_count(self):
        """Retorna el número de challenges resueltos por el equipo"""
        from challenges.models import Submission
        return Submission.objects.filter(team=self, is_correct=True).values('challenge').distinct().count()
    
    def get_first_bloods_count(self):
        """Retorna el número de first bloods conseguidos por el equipo"""
        from challenges.models import FirstBlood
        return FirstBlood.objects.filter(team=self).count()
    
    @property
    def score(self):
        """Alias para total_score para compatibilidad con templates"""
        return self.total_score
    
    def update_score(self):
        """Actualiza la puntuación total del equipo sumando los puntos de todos sus miembros"""
        from challenges.models import Submission, FirstBlood
        
        total_points = 0
        
        # Sumar puntos de cada miembro del equipo
        for member in self.members.all():
            # Puntos de challenges resueltos por el miembro
            member_challenge_points = Submission.objects.filter(
                team=self,
                submitted_by=member,
                is_correct=True
            ).aggregate(
                total=models.Sum('challenge__points')
            )['total'] or 0
            
            # Puntos bonus de first bloods del miembro
            member_fb_points = FirstBlood.objects.filter(
                team=self,
                achieved_by=member
            ).aggregate(
                total=models.Sum('bonus_points')
            )['total'] or 0
            
            total_points += member_challenge_points + member_fb_points
        
        self.total_score = total_points
        self.save()
