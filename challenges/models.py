from django.db import models
from teams.models import Team
from django.utils import timezone
import uuid

class Category(models.Model):
    """Categorías de los challenges (Web, Crypto, Forensics, etc.)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, default="", verbose_name="Descripción")
    icon = models.CharField(max_length=50, default="🔐", verbose_name="Icono")
    color = models.CharField(max_length=7, default="#00FF00", verbose_name="Color")
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
    
    def __str__(self):
        return self.name

class Challenge(models.Model):
    """Modelo para los desafíos del CTF"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='challenges', verbose_name="Categoría")
    points = models.IntegerField(default=100, verbose_name="Puntos")
    flag = models.CharField(max_length=200, verbose_name="Flag")
    files = models.FileField(upload_to='challenge_files/', null=True, blank=True, verbose_name="Archivos")
    hints = models.TextField(blank=True, verbose_name="Pistas")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    
    class Meta:
        verbose_name = "Challenge"
        verbose_name_plural = "Challenges"
        ordering = ['category', 'points']
    
    def __str__(self):
        return f"{self.title} ({self.points}pts)"
    
    def get_solve_count(self):
        """Retorna el número de equipos que han resuelto este challenge"""
        return Submission.objects.filter(challenge=self, is_correct=True).values('team').distinct().count()

class Submission(models.Model):
    """Modelo para los intentos de resolver challenges"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='submissions', verbose_name="Equipo")
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='submissions', verbose_name="Challenge")
    flag_submitted = models.CharField(max_length=200, verbose_name="Flag enviada")
    is_correct = models.BooleanField(default=False, verbose_name="¿Es correcta?")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de envío")
    submitted_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='submissions', verbose_name="Enviado por")
    
    class Meta:
        verbose_name = "Submission"
        verbose_name_plural = "Submissions"
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.team.name} - {self.challenge.title} ({'✓' if self.is_correct else '✗'})"

class FirstBlood(models.Model):
    """Modelo para registrar las primeras sangres"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='first_bloods', verbose_name="Equipo")
    challenge = models.OneToOneField(Challenge, on_delete=models.CASCADE, related_name='first_blood', verbose_name="Challenge")
    achieved_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de logro")
    bonus_points = models.IntegerField(default=50, verbose_name="Puntos bonus")
    achieved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='first_bloods', verbose_name="Logrado por")
    
    class Meta:
        verbose_name = "First Blood"
        verbose_name_plural = "First Bloods"
        ordering = ['-achieved_at']
    
    def __str__(self):
        return f"🩸 {self.team.name} - {self.challenge.title}"
