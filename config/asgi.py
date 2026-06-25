import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.forum.routing import websocket_urlpatterns as forum_ws
from apps.marketplace.routing import websocket_urlpatterns as marketplace_ws

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(forum_ws + marketplace_ws)
    ),
})
