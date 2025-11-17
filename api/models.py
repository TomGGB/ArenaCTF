"""
Modelos para la API
"""
from django.db import models
from django.conf import settings
import secrets


class APIToken(models.Model):
    """
    Token de API para autenticación
    Similar a CTFd tokens
    """
    key = models.CharField(max_length=64, unique=True, primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_tokens'
    )
    description = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'API Token'
        verbose_name_plural = 'API Tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.description or 'Token'}"
    
    def save(self, *args, **kwargs):
        """Generar token si no existe"""
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_key():
        """Generar un token único"""
        return secrets.token_urlsafe(48)
    
    def update_last_used(self):
        """Actualizar la fecha de último uso"""
        from django.utils import timezone
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])
