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
