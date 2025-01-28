"""
ASGI config for myproject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/

"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from your_app.consumers import ChatConsumer  # Replace `your_app` with your actual app name

# Set the default settings module for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')  # Replace `myproject` with your project name

# Get the Django ASGI application
django_asgi_app = get_asgi_application()

# Define the ASGI application with ProtocolTypeRouter
application = ProtocolTypeRouter({
    "http": django_asgi_app,  # HTTP requests will be handled by the Django ASGI application
    "websocket": AuthMiddlewareStack(  # WebSocket connections will use authentication middleware
        URLRouter(
            [
                path('ws/chat/<str:anam>/', ChatConsumer.as_asgi()),
                # path('ws/chat/<str:room_name>/', ChatConsumer.as_asgi()),  # Define WebSocket route
            ]
        )
    ),
})
