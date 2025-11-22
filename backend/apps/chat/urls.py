from django.urls import path
from .views import (
    ChatRoomListView, ChatRoomDetailView, SendMessageView,
    MarkMessagesReadView
)

urlpatterns = [
    path('rooms/', ChatRoomListView.as_view(), name='chat-rooms'),
    path('rooms/<uuid:room_id>/', ChatRoomDetailView.as_view(), name='chat-room-detail'),
    path('rooms/<uuid:room_id>/send/', SendMessageView.as_view(), name='send-message'),
    path('rooms/<uuid:room_id>/read/', MarkMessagesReadView.as_view(), name='mark-read'),
]