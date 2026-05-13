from django.contrib import admin
from .models import Conversation, ConversationMember, DirectMessage, GroupMessage, UserProfile

admin.site.register(UserProfile)
admin.site.register(Conversation)
admin.site.register(ConversationMember)
admin.site.register(DirectMessage)
admin.site.register(GroupMessage)
