from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import ChatRoom, Message, TypingStatus
from .serializers import (
    ChatRoomSerializer,
    ChatRoomDetailSerializer,
    MessageSerializer,
)

from apps.authentication.models import User


# ============================================================
# GET ALL CHAT ROOMS FOR LOGGED-IN USER
# ============================================================

class ChatRoomListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(
            participant_1=user
        ) | ChatRoom.objects.filter(
            participant_2=user
        )


# ============================================================
# CHAT ROOM DETAIL (INCLUDING ALL MESSAGES)
# ============================================================

class ChatRoomDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomDetailSerializer
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(
            participant_1=user
        ) | ChatRoom.objects.filter(
            participant_2=user
        )


# ============================================================
# SEND A MESSAGE VIA REST (not websocket)
# ============================================================

class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)

        # Validate user is a participant
        if request.user not in [room.participant_1, room.participant_2]:
            return Response({"error": "Not allowed"}, status=403)

        message_text = request.data.get("message_text")
        message_type = request.data.get("message_type", "text")
        shared_content_id = request.data.get("shared_content_id")

        if not message_text and message_type == "text":
            return Response({"error": "Message text is required"}, status=400)

        message = Message.objects.create(
            chat_room=room,
            sender=request.user,
            message_text=message_text,
            message_type=message_type,
            shared_content_id=shared_content_id
        )

        # Update room last message info
        room.last_message_text = message_text[:100] if message_text else ""
        room.last_message_at = timezone.now()
        room.last_message_sender = request.user
        room.save()

        return Response(MessageSerializer(message).data, status=201)


# ============================================================
# MARK ALL MESSAGES AS READ IN A ROOM
# ============================================================

class MarkMessagesReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)

        # Ensure user is in the chat room
        if request.user not in [room.participant_1, room.participant_2]:
            return Response({"error": "Not allowed"}, status=403)

        messages = Message.objects.filter(
            chat_room=room,
            is_read=False
        ).exclude(sender=request.user)

        updated = messages.update(is_read=True, read_at=timezone.now())

        return Response(
            {"message": f"{updated} messages marked as read"},
            status=200
        )
