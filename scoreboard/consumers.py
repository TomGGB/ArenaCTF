import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ScoreboardConsumer(AsyncWebsocketConsumer):
    """Consumer para actualizaciones en tiempo real del scoreboard"""
    
    async def connect(self):
        """Conectar al grupo de scoreboard"""
        self.room_group_name = 'scoreboard'
        
        # Unirse al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Desconectar del grupo"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Recibir mensaje del WebSocket"""
        pass
    
    async def flag_solved_notification(self, event):
        """Enviar notificación de flag resuelta"""
        await self.send(text_data=json.dumps({
            'type': 'flag_solved',
            'team': event['team'],
            'challenge': event['challenge'],
            'points': event['points'],
            'color': event['color'],
            'is_first_blood': event.get('is_first_blood', False),
        }))
    
    async def first_blood_notification(self, event):
        """Enviar notificación de first blood"""
        await self.send(text_data=json.dumps({
            'type': 'first_blood',
            'team': event['team'],
            'challenge': event['challenge'],
            'color': event['color'],
        }))
    
    async def scoreboard_update(self, event):
        """Enviar actualización del scoreboard"""
        await self.send(text_data=json.dumps({
            'type': 'scoreboard_update',
            'scoreboard': event['scoreboard'],
        }))
    
    async def rank_change_notification(self, event):
        """Enviar notificación de cambio de ranking"""
        await self.send(text_data=json.dumps({
            'type': 'rank_change',
            'team': event['team'],
            'old_rank': event['old_rank'],
            'new_rank': event['new_rank'],
            'color': event['color'],
        }))
    
    async def display_data_update(self, event):
        """Enviar actualización completa de datos del display"""
        message = {
            'type': 'display_data_update',
            'teams': event['teams'],
            'recent_submissions': event.get('recent_submissions', []),
            'first_bloods': event.get('first_bloods', []),
            'timeline': event.get('timeline', {}),
        }
        
        # Agregar información del evento si existe
        if 'event_type' in event:
            message['event_type'] = event['event_type']
            message['event_data'] = event.get('event_data', {})
        
        await self.send(text_data=json.dumps(message))
    
    async def ctf_time_warning(self, event):
        """Enviar advertencia de tiempo restante del CTF"""
        await self.send(text_data=json.dumps({
            'type': 'ctf_time_warning',
            'message': event['message'],
            'minutes_left': event['minutes_left'],
        }))
    
    async def ctf_ended(self, event):
        """Enviar notificación de CTF finalizado"""
        await self.send(text_data=json.dumps({
            'type': 'ctf_ended',
            'message': event['message'],
        }))
    
    async def notification(self, event):
        """Enviar notificación genérica"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification_type': event.get('notification_type', 'info'),
            'message': event['message'],
        }))
    
    async def achievement_unlocked(self, event):
        """Enviar notificación de logro desbloqueado"""
        await self.send(text_data=json.dumps({
            'type': 'achievement_unlocked',
            'message': event['message'],
            'achievement': event.get('achievement', ''),
        }))
    
    async def flag_solved(self, event):
        """Enviar notificación de flag resuelta (para pruebas)"""
        await self.send(text_data=json.dumps({
            'type': 'flag_solved',
            'message': event['message'],
            'team': event.get('team', ''),
            'challenge': event.get('challenge', ''),
            'points': event.get('points', 0),
        }))
    
    async def first_blood(self, event):
        """Enviar notificación de first blood (para pruebas)"""
        await self.send(text_data=json.dumps({
            'type': 'first_blood',
            'message': event['message'],
            'team': event.get('team', ''),
            'challenge': event.get('challenge', ''),
        }))
    
    async def rank_change(self, event):
        """Enviar notificación de cambio de ranking (para pruebas)"""
        await self.send(text_data=json.dumps({
            'type': 'rank_change',
            'message': event['message'],
            'team': event.get('team', ''),
            'old_rank': event.get('old_rank', 0),
            'new_rank': event.get('new_rank', 0),
        }))
    
    async def custom_announcement(self, event):
        """Enviar anuncio personalizado"""
        await self.send(text_data=json.dumps({
            'type': 'custom_announcement',
            'title': event.get('title', ''),
            'message': event['message'],
            'notification_type': event.get('notification_type', 'info'),
        }))
