from django.urls import path
from .views import (
    ChatRoomListView,
    ChatRoomDetailView,
    SendMessageView,
    MarkMessagesReadView,
)

urlpatterns = [
    # -------------------------------------
    # Chat Rooms
    # -------------------------------------
    path("rooms/", ChatRoomListView.as_view(), name="chat-rooms"),
    path("rooms/<uuid:room_id>/", ChatRoomDetailView.as_view(), name="chat-room-detail"),

    # -------------------------------------
    # Messaging
    # -------------------------------------
    path("rooms/<uuid:room_id>/send/", SendMessageView.as_view(), name="send-message"),
    path("rooms/<uuid:room_id>/read/", MarkMessagesReadView.as_view(), name="mark-read"),
]
