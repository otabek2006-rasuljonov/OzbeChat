import json
from urllib.parse import parse_qs

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from .models import Conversation, ConversationMember, DirectMessage, GroupMessage

INITIAL_MESSAGE_LIMIT = 20


class ChatConsumer(WebsocketConsumer):
    def _extract_token(self):
        headers = {key.decode().lower(): value.decode() for key, value in self.scope.get('headers', [])}
        auth_header = headers.get('authorization', '')
        if auth_header.lower().startswith('bearer '):
            return auth_header.split(' ', 1)[1].strip()
        return parse_qs(self.scope['query_string'].decode()).get('token', [None])[0]

    def connect(self):
        token = self._extract_token()
        if not token:
            self.close()
            return

        try:
            access_token = AccessToken(token)
            self.user = User.objects.get(id=access_token['user_id'])
        except Exception:
            self.close()
            return

        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        try:
            self.conversation = Conversation.objects.get(id=self.conversation_id)
            self.membership = ConversationMember.objects.get(
                conversation=self.conversation,
                user=self.user,
                is_active=True,
            )
        except (Conversation.DoesNotExist, ConversationMember.DoesNotExist):
            self.close()
            return

        self.room_group_name = f'conversation_{self.conversation_id}'

        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

        if hasattr(self.user, 'profile'):
            self.user.profile.status = 'online'
            self.user.profile.last_seen = timezone.now()
            self.user.profile.save(update_fields=['status', 'last_seen'])

        if self.conversation.conversation_type == 'direct':
            messages = self.conversation.direct_messages.select_related('sender').order_by('-created_at')[
                :INITIAL_MESSAGE_LIMIT
            ]
            message_type = 'direct'
        else:
            messages = self.conversation.group_messages.select_related('sender').order_by('-created_at')[
                :INITIAL_MESSAGE_LIMIT
            ]
            message_type = 'group'

        for msg in reversed(list(messages)):
            self.send(
                text_data=json.dumps(
                    {
                        'id': msg.id,
                        'type': message_type,
                        'username': msg.sender.username,
                        'message': msg.text,
                        'time': msg.created_at.strftime('%H:%M'),
                    }
                )
            )

    def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

        if hasattr(self, 'user') and hasattr(self.user, 'profile'):
            self.user.profile.status = 'offline'
            self.user.profile.last_seen = timezone.now()
            self.user.profile.save(update_fields=['status', 'last_seen'])

    def receive(self, text_data):
        if not hasattr(self, 'conversation'):
            return

        data = json.loads(text_data)
        message_text = data.get('message', '').strip()
        if not message_text:
            return

        if self.conversation.conversation_type == 'direct':
            msg = DirectMessage.objects.create(
                sender=self.user,
                conversation=self.conversation,
                text=message_text,
            )
            message_type = 'direct'
        else:
            msg = GroupMessage.objects.create(
                sender=self.user,
                conversation=self.conversation,
                text=message_text,
            )
            message_type = 'group'

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': msg.id,
                'message_type': message_type,
                'username': self.user.username,
                'message': message_text,
                'time': msg.created_at.strftime('%H:%M'),
            },
        )

    def chat_message(self, event):
        self.send(
            text_data=json.dumps(
                {
                    'id': event['id'],
                    'type': event['message_type'],
                    'username': event['username'],
                    'message': event['message'],
                    'time': event['time'],
                }
            )
        )
