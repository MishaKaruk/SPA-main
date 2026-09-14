from django.urls import path

from .consumers import CommentsConsumer

websocket_urlpatterns = [
    path('ws/comments/', CommentsConsumer.as_asgi()),
    path('ws/comments/<int:thread_id>/', CommentsConsumer.as_asgi()),
]
