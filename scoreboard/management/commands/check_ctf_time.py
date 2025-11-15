from django.core.management.base import BaseCommand
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from scoreboard.models import CTFConfig
from datetime import timedelta


class Command(BaseCommand):
    help = 'Verifica el tiempo restante del CTF y envía notificaciones'

    def handle(self, *args, **options):
        config = CTFConfig.get_config()
        
        if not config.end_time:
            self.stdout.write(self.style.WARNING('No hay end_time configurado'))
            return
        
        now = timezone.now()
        time_left = config.end_time - now
        
        if time_left.total_seconds() <= 0:
            self.stdout.write(self.style.ERROR('El CTF ha finalizado'))
            # Enviar notificación de finalización
            self.send_ctf_ended_notification()
            return
        
        minutes_left = int(time_left.total_seconds() / 60)
        
        # Enviar advertencias en momentos específicos
        warning_times = [60, 30, 15, 10, 5, 1]  # minutos
        
        for warning_time in warning_times:
            if minutes_left == warning_time:
                self.send_time_warning(minutes_left)
                self.stdout.write(
                    self.style.SUCCESS(f'Enviada advertencia: {minutes_left} minutos restantes')
                )
                return
        
        self.stdout.write(
            self.style.SUCCESS(f'Tiempo restante: {minutes_left} minutos')
        )
    
    def send_time_warning(self, minutes_left):
        """Enviar advertencia de tiempo por WebSocket"""
        channel_layer = get_channel_layer()
        
        if minutes_left >= 60:
            message = f'⏰ ¡Atención! Quedan {minutes_left // 60} hora(s) para que finalice el CTF'
        elif minutes_left > 1:
            message = f'⏰ ¡Atención! Quedan {minutes_left} minutos para que finalice el CTF'
        else:
            message = '⏰ ¡ÚLTIMO MINUTO! El CTF está por finalizar'
        
        async_to_sync(channel_layer.group_send)(
            'scoreboard',
            {
                'type': 'ctf_time_warning',
                'message': message,
                'minutes_left': minutes_left,
            }
        )
    
    def send_ctf_ended_notification(self):
        """Enviar notificación de CTF finalizado"""
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            'scoreboard',
            {
                'type': 'ctf_ended',
                'message': '🏁 ¡El CTF ha finalizado! Ya no se aceptan más submissions.',
            }
        )
