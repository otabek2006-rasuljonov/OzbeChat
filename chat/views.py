from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Conversation, ConversationMember, DirectMessage, GroupMessage


def _direct_key(user_a: User, user_b: User) -> str:
    first, second = sorted([user_a.username.lower(), user_b.username.lower()])
    return f'{first}:{second}'


def _serialize_message(message_obj, message_type: str):
    return {
        'id': message_obj.id,
        'type': message_type,
        'sender': message_obj.sender.username,
        'text': message_obj.text,
        'created_at': message_obj.created_at,
    }


def _conversation_queryset_for_user(user):
    return Conversation.objects.filter(
        memberships__user=user,
        memberships__is_active=True,
    ).distinct().order_by('-created_at')


def _conversation_payload(conversation, current_user):
    active_members = conversation.memberships.filter(is_active=True).select_related('user', 'user__profile')
    members = [
        {
            'username': m.user.username,
            'role': m.role,
            'is_online': getattr(getattr(m.user, 'profile', None), 'status', 'offline') == 'online',
        }
        for m in active_members
    ]

    if conversation.conversation_type == 'direct':
        last_message = conversation.direct_messages.order_by('-created_at').first()
        unread_count = conversation.direct_messages.filter(
            created_at__gt=conversation.memberships.get(user=current_user).last_read_at
        ).exclude(sender=current_user).count()
    else:
        last_message = conversation.group_messages.order_by('-created_at').first()
        unread_count = conversation.group_messages.filter(
            created_at__gt=conversation.memberships.get(user=current_user).last_read_at
        ).exclude(sender=current_user).count()

    return {
        'id': conversation.id,
        'conversation_type': conversation.conversation_type,
        'name': conversation.name,
        'members': members,
        'unread_count': unread_count,
        'last_message': _serialize_message(last_message, conversation.conversation_type) if last_message else None,
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')

    if not username or not password:
        return Response({'error': 'Username va parol majburiy'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Bu username band'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    token = RefreshToken.for_user(user)
    return Response({'access': str(token.access_token), 'refresh': str(token)}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'error': 'Xato login yoki parol'}, status=status.HTTP_400_BAD_REQUEST)

    if hasattr(user, 'profile'):
        user.profile.status = 'online'
        user.profile.last_seen = timezone.now()
        user.profile.save(update_fields=['status', 'last_seen'])

    token = RefreshToken.for_user(user)
    return Response({'access': str(token.access_token), 'refresh': str(token)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_search(request):
    query = request.GET.get('q', '').strip()
    users = User.objects.exclude(id=request.user.id)
    if query:
        users = users.filter(username__icontains=query)

    users = users.select_related('profile').order_by('username')[:30]
    data = [
        {
            'id': user.id,
            'username': user.username,
            'bio': getattr(user.profile, 'bio', ''),
            'is_online': getattr(user.profile, 'status', 'offline') == 'online',
        }
        for user in users
    ]
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversations(request):
    conversation_list = _conversation_queryset_for_user(request.user)
    payload = [_conversation_payload(conversation, request.user) for conversation in conversation_list]
    return Response(payload)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_conversation(request):
    username = request.data.get('username', '').strip()
    if not username:
        return Response({'error': 'username majburiy'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        target = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'Foydalanuvchi topilmadi'}, status=status.HTTP_404_NOT_FOUND)

    if target.id == request.user.id:
        return Response({'error': 'Ozingiz bilan chat boshlay olmaysiz'}, status=status.HTTP_400_BAD_REQUEST)

    direct_key = _direct_key(request.user, target)
    conversation, _ = Conversation.objects.get_or_create(
        direct_key=direct_key,
        defaults={
            'conversation_type': 'direct',
            'created_by': request.user,
            'name': '',
        },
    )

    for member in (request.user, target):
        membership, created = ConversationMember.objects.get_or_create(
            conversation=conversation,
            user=member,
            defaults={'role': 'member'},
        )
        if not created and not membership.is_active:
            membership.is_active = True
            membership.left_at = None
            membership.save(update_fields=['is_active', 'left_at'])

    return Response(_conversation_payload(conversation, request.user), status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    name = request.data.get('name', '').strip()
    usernames = request.data.get('members', [])

    if not name:
        return Response({'error': 'Guruh nomi majburiy'}, status=status.HTTP_400_BAD_REQUEST)

    conversation = Conversation.objects.create(
        conversation_type='group',
        name=name,
        created_by=request.user,
    )

    ConversationMember.objects.create(
        conversation=conversation,
        user=request.user,
        role='admin',
    )

    if usernames:
        members = User.objects.filter(username__in=usernames).exclude(id=request.user.id)
        ConversationMember.objects.bulk_create(
            [
                ConversationMember(
                    conversation=conversation,
                    user=member,
                    role='member',
                )
                for member in members
            ],
            ignore_conflicts=True,
        )

    return Response(_conversation_payload(conversation, request.user), status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_group_member(request, conversation_id):
    username = request.data.get('username', '').strip()
    if not username:
        return Response({'error': 'username majburiy'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        conversation = Conversation.objects.get(id=conversation_id, conversation_type='group')
    except Conversation.DoesNotExist:
        return Response({'error': 'Guruh topilmadi'}, status=status.HTTP_404_NOT_FOUND)

    try:
        actor_membership = ConversationMember.objects.get(conversation=conversation, user=request.user, is_active=True)
    except ConversationMember.DoesNotExist:
        return Response({'error': 'Ruxsat yoq'}, status=status.HTTP_403_FORBIDDEN)

    if actor_membership.role != 'admin':
        return Response({'error': 'Faqat admin azo qosha oladi'}, status=status.HTTP_403_FORBIDDEN)

    try:
        target = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'Foydalanuvchi topilmadi'}, status=status.HTTP_404_NOT_FOUND)

    membership, created = ConversationMember.objects.get_or_create(
        conversation=conversation,
        user=target,
        defaults={'role': 'member'},
    )
    if not created and not membership.is_active:
        membership.is_active = True
        membership.left_at = None
        membership.save(update_fields=['is_active', 'left_at'])

    return Response({'conversation_id': conversation.id, 'username': target.username})


def _delete_message_for_user(user, message_id):
    direct_message = DirectMessage.objects.filter(id=message_id).select_related('conversation').first()
    group_message = GroupMessage.objects.filter(id=message_id).select_related('conversation').first()

    candidates = [message for message in [direct_message, group_message] if message is not None]
    if not candidates:
        return Response({'error': 'Xabar topilmadi'}, status=status.HTTP_404_NOT_FOUND)

    target_message = next((msg for msg in candidates if msg.sender_id == user.id), None)
    if target_message is None:
        return Response({'error': 'Siz faqat oz xabaringizni ochira olasiz'}, status=status.HTTP_403_FORBIDDEN)

    target_message.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def messages(request, conversation_id):
    if request.method == 'DELETE':
        return _delete_message_for_user(request.user, conversation_id)

    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        return Response({'error': 'Suhbat topilmadi'}, status=status.HTTP_404_NOT_FOUND)

    try:
        membership = ConversationMember.objects.get(conversation=conversation, user=request.user, is_active=True)
    except ConversationMember.DoesNotExist:
        return Response({'error': 'Ruxsat yoq'}, status=status.HTTP_403_FORBIDDEN)

    if conversation.conversation_type == 'direct':
        queryset = conversation.direct_messages.select_related('sender').order_by('created_at')
        data = [_serialize_message(message, 'direct') for message in queryset]
    else:
        queryset = conversation.group_messages.select_related('sender').order_by('created_at')
        data = [_serialize_message(message, 'group') for message in queryset]

    membership.last_read_at = timezone.now()
    membership.save(update_fields=['last_read_at'])
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_conversation(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        return Response({'error': 'Suhbat topilmadi'}, status=status.HTTP_404_NOT_FOUND)

    try:
        membership = ConversationMember.objects.get(conversation=conversation, user=request.user, is_active=True)
    except ConversationMember.DoesNotExist:
        return Response({'error': 'Siz bu suhbatda yoqsiz'}, status=status.HTTP_400_BAD_REQUEST)

    if conversation.conversation_type == 'group' and membership.role == 'admin':
        has_other_admins = ConversationMember.objects.filter(
            conversation=conversation,
            role='admin',
            is_active=True,
        ).exclude(user=request.user).exists()
        if not has_other_admins:
            next_member = ConversationMember.objects.filter(
                conversation=conversation,
                is_active=True,
            ).exclude(user=request.user).first()
            if next_member:
                next_member.role = 'admin'
                next_member.save(update_fields=['role'])

    membership.is_active = False
    membership.left_at = timezone.now()
    membership.save(update_fields=['is_active', 'left_at'])

    return Response({'status': 'left'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_message(request, message_id):
    return _delete_message_for_user(request.user, message_id)


# Backward-compatible wrappers
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users(request):
    return users_search(request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rooms(request):
    return conversations(request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_room(request):
    name = request.data.get('name', '').strip()
    if not name:
        return Response({'error': 'Nom kiriting'}, status=status.HTTP_400_BAD_REQUEST)

    conversation = Conversation.objects.create(
        conversation_type='group',
        name=name,
        created_by=request.user,
    )
    ConversationMember.objects.create(
        conversation=conversation,
        user=request.user,
        role='admin',
    )
    return Response({'name': conversation.name}, status=status.HTTP_201_CREATED)
