from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Conversation, ConversationMember, DirectMessage


class ChatApiTests(APITestCase):
    def _register(self, username, password='strong-pass-123'):
        response = self.client.post('/api/auth/register/', {'username': username, 'password': password}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data['access']

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_start_direct_conversation_by_username(self):
        token_a = self._register('ali')
        self._register('vali')
        self._auth(token_a)

        response = self.client.post('/api/conversations/start/', {'username': 'vali'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['conversation_type'], 'direct')

        response_again = self.client.post('/api/conversations/start/', {'username': 'vali'}, format='json')
        self.assertEqual(response_again.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_again.data['id'], response.data['id'])

        self.assertEqual(Conversation.objects.filter(conversation_type='direct').count(), 1)
        self.assertEqual(
            ConversationMember.objects.filter(conversation_id=response.data['id'], is_active=True).count(),
            2,
        )

    def test_group_create_add_member_and_leave(self):
        admin_token = self._register('admin_user')
        self._register('member_user')
        self._auth(admin_token)

        create_response = self.client.post(
            '/api/groups/create/',
            {'name': 'Python Group', 'members': []},
            format='json',
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        conversation_id = create_response.data['id']

        add_response = self.client.post(
            f'/api/groups/{conversation_id}/add-member/',
            {'username': 'member_user'},
            format='json',
        )
        self.assertEqual(add_response.status_code, status.HTTP_200_OK)

        leave_response = self.client.post(f'/api/conversations/{conversation_id}/leave/')
        self.assertEqual(leave_response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            ConversationMember.objects.get(conversation_id=conversation_id, user__username='admin_user').is_active
        )

    def test_get_messages_marks_as_read_and_delete_own_message(self):
        token_a = self._register('user_a')
        self._register('user_b')
        self._auth(token_a)
        start_response = self.client.post('/api/conversations/start/', {'username': 'user_b'}, format='json')
        conversation_id = start_response.data['id']
        user_a = User.objects.get(username='user_a')
        message = DirectMessage.objects.create(conversation_id=conversation_id, sender=user_a, text='salom')

        messages_response = self.client.get(f'/api/messages/{conversation_id}/')
        self.assertEqual(messages_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(messages_response.data), 1)

        membership = ConversationMember.objects.get(conversation_id=conversation_id, user=user_a)
        self.assertIsNotNone(membership.last_read_at)

        delete_response = self.client.delete(f'/api/messages/{message.id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(DirectMessage.objects.filter(id=message.id).exists())
