from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class UserProfile(models.Model):
    STATUS_CHOICES = (
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('away', 'Away'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    last_seen = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username


class Conversation(models.Model):
    CONVERSATION_TYPES = (
        ('direct', 'Direct'),
        ('group', 'Group'),
    )

    conversation_type = models.CharField(max_length=10, choices=CONVERSATION_TYPES)
    name = models.CharField(max_length=255, blank=True)
    direct_key = models.CharField(max_length=255, blank=True, null=True, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f'Conversation {self.id}'


class ConversationMember(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
    )

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversation_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_read_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('conversation', 'user')


class DirectMessage(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='direct_messages',
        limit_choices_to={'conversation_type': 'direct'},
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_direct_messages')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class GroupMessage(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='group_messages',
        limit_choices_to={'conversation_type': 'group'},
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_group_messages')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
