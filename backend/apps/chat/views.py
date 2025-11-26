from rest_framework import generics, status, serializers
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view

from .models import ChatRoom, Message
from .serializers import (
    ChatRoomSerializer,
    ChatRoomDetailSerializer,
    MessageSerializer,
)


# ============================================================
# SERIALIZER FOR SEND MESSAGE ENDPOINT
# ============================================================
class SendMessageSerializer(serializers.Serializer):
    message_text = serializers.CharField(required=False, allow_blank=True)
    message_type = serializers.ChoiceField(
        choices=["text", "movie_share", "review_share"], default="text"
    )
    shared_content_id = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )


# ============================================================
# GET ALL CHAT ROOMS
# ============================================================

@extend_schema_view(
    get=extend_schema(
        tags=["Chat"],
        responses={200: ChatRoomSerializer(many=True)}
    )
)
class ChatRoomListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(
            models.Q(participant_1=user) | models.Q(participant_2=user)
        ).distinct()


# ============================================================
# GET CHAT ROOM DETAIL (with message history)
# ============================================================

@extend_schema_view(
    get=extend_schema(
        tags=["Chat"],
        responses={200: ChatRoomDetailSerializer}
    )
)
class ChatRoomDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomDetailSerializer
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(
            models.Q(participant_1=user) | models.Q(participant_2=user)
        ).distinct()


# ============================================================
# SEND MESSAGE (No warnings)
# ============================================================

@extend_schema_view(
    post=extend_schema(
        tags=["Chat"],
        request=SendMessageSerializer,
        responses={201: MessageSerializer}
    )
)
class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)

        # Check room membership
        if request.user not in [room.participant_1, room.participant_2]:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        message_text = data.get("message_text", "")
        message_type = data.get("message_type", "text")
        shared_content_id = data.get("shared_content_id")

        if message_type == "text" and not message_text:
            return Response({"error": "Message text required"}, status=400)

        # Create message
        message = Message.objects.create(
            chat_room=room,
            sender=request.user,
            message_text=message_text,
            message_type=message_type,
            shared_content_id=shared_content_id,
        )

        # Update chat room metadata
        room.last_message_text = (message_text or "")[:100]
        room.last_message_at = timezone.now()
        room.last_message_sender = request.user
        room.save(update_fields=["last_message_text", "last_message_at", "last_message_sender"])

        return Response(
            MessageSerializer(message, context={"request": request}).data,
            status=status.HTTP_201_CREATED
        )


# ============================================================
# MARK ALL MESSAGES AS READ
# ============================================================

@extend_schema_view(
    post=extend_schema(
        tags=["Chat"],
        request=None,
        responses={200: OpenApiResponse(
            description="Count of updated messages",
            response={"type": "object", "properties": {"updated": {"type": "integer"}}}
        )}
    )
)
class MarkMessagesReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)

        if request.user not in [room.participant_1, room.participant_2]:
            return Response({"error": "Not allowed"}, status=403)

        qs = Message.objects.filter(
            chat_room=room, is_read=False
        ).exclude(sender=request.user)

        updated = qs.update(is_read=True, read_at=timezone.now())

        return Response({"updated": updated}, status=200)

