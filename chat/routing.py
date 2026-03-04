from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # \w+ o'rniga [^/]+ qo'shildi
    re_path(r'ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
]