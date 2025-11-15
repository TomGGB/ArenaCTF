from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class CTFConfig(models.Model):
    """Configuración global del CTF"""
    name = models.CharField(max_length=200, default="Mi CTF", verbose_name="Nombre del CTF")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="Inicio del CTF")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Fin del CTF")
    is_active = models.BooleanField(default=False, verbose_name="CTF Activo")
    first_blood_points = models.IntegerField(default=50, verbose_name="Puntos de First Blood")
    timezone = models.CharField(max_length=100, default="America/Argentina/Buenos_Aires", verbose_name="Zona Horaria")
    
    class Meta:
        verbose_name = "Configuración CTF"
        verbose_name_plural = "Configuración CTF"
    
    def __str__(self):
        return f"CTF Config - {'Activo' if self.is_active else 'Inactivo'}"
    
    @classmethod
    def get_config(cls):
        """Obtener o crear la configuración"""
        config, created = cls.objects.get_or_create(pk=1)
        return config


class Achievement(models.Model):
    """Logro conseguido por un equipo o usuario"""
    CATEGORY_CHOICES = [
        ('team', 'Equipo'),
        ('individual', 'Individual'),
    ]
    
    code = models.CharField(max_length=50, verbose_name="Código del Logro")
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='achievements', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements', null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='team')
    earned_at = models.DateTimeField(auto_now_add=True, verbose_name="Conseguido el")
    
    class Meta:
        verbose_name = "Logro"
        verbose_name_plural = "Logros"
        unique_together = [['code', 'team'], ['code', 'user']]
        ordering = ['-earned_at']
    
    def __str__(self):
        from .achievements import get_achievement_info
        info = get_achievement_info(self.code)
        name = info.name if info else self.code
        
        if self.team:
            return f"{name} - {self.team.name}"
        elif self.user:
            return f"{name} - {self.user.username}"
        return name
    
    def get_info(self):
        """Obtiene la información completa del logro"""
        from .achievements import get_achievement_info
        return get_achievement_info(self.code)
