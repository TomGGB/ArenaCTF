from django.db import models
from django.utils import timezone

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
