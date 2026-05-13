from django.contrib import admin
from django.urls import path

from chat import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/register/', views.register),
    path('api/auth/login/', views.login_view),
    path('api/users/search/', views.users_search),
    path('api/conversations/', views.conversations),
    path('api/conversations/start/', views.start_conversation),
    path('api/groups/create/', views.create_group),
    path('api/groups/<int:conversation_id>/add-member/', views.add_group_member),
    path('api/messages/<int:resource_id>/', views.messages),
    path('api/conversations/<int:conversation_id>/leave/', views.leave_conversation),
    # Backward-compatible legacy routes
    path('api/register/', views.register),
    path('api/login/', views.login_view),
    path('api/rooms/', views.rooms),
    path('api/rooms/create/', views.create_room),
    path('api/users/', views.users),
]
