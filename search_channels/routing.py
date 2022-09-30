from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('test', consumers.SimpleConsumer.as_asgi())
]
