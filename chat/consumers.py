import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
from .models import Message, Room
from django.utils import timezone

class ChatConsumer(WebsocketConsumer):

    def connect(self):
        # Token tekshirish
        token = self.scope['query_string'].decode().split('token=')[-1]
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            self.user = User.objects.get(id=user_id)
        except Exception:
            self.close()
            return

        # Xona nomini URL dan olamiz
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        
        # Xona yo'q bo'lsa yaratamiz
        self.room, _ = Room.objects.get_or_create(name=self.room_name)

        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )
        self.accept()

        # Eski xabarlarni yuborish
        messages = Message.objects.filter(room=self.room).order_by('created_at')[:20]
        for msg in messages:
            self.send(text_data=json.dumps({
                'username': msg.user.username,
                'message': msg.text,
                'time': msg.created_at.strftime('%H:%M')
            }))

    def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            async_to_sync(self.channel_layer.group_discard)(
                self.room_name,
                self.channel_name
            )

    def receive(self, text_data):
        data = json.loads(text_data)
        msg = Message.objects.create(
            user=self.user,
            room=self.room,
            text=data['message']
        )
        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                'type': 'chat_message',
                'username': self.user.username,
                'message': data['message'],
                'time': msg.created_at.strftime('%H:%M')
            }
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'username': event['username'],
            'message': event['message'],
            'time': event['time']
    }))
        