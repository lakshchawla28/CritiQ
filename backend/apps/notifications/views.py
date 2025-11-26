from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)

from .models import Notification, PushToken
from .serializers import NotificationSerializer, PushTokenSerializer


# =====================================================================
#                          NOTIFICATION VIEWSET
# =====================================================================

@extend_schema_view(
    retrieve=extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                type={"type": "string", "format": "uuid"},
                location="path",
                description="Notification ID",
            )
        ]
    ),
    mark_read=extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                type={"type": "string", "format": "uuid"},
                location="path",
                description="Notification ID",
            )
        ]
    ),
    delete_notification=extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                type={"type": "string", "format": "uuid"},
                location="path",
                description="Notification ID",
            )
        ]
    ),
)
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user notifications.
    Uses router-generated `.../notifications/<id>/` paths.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @extend_schema(
        summary="Unread Notifications Count",
        description="Returns the number of unread notifications for the user.",
    )
    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({"unread_count": count})

    @extend_schema(summary="Mark a notification as read")
    @action(detail=True, methods=["post"])
    def mark_read(self, request, id=None):
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({"status": "notification marked as read"})

    @extend_schema(summary="Mark all notifications as read")
    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return Response({"status": "all notifications marked as read"})

    @extend_schema(summary="Delete a notification")
    @action(detail=True, methods=["delete"])
    def delete_notification(self, request, id=None):
        notification = self.get_object()
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(summary="Clear all notifications")
    @action(detail=False, methods=["delete"])
    def clear_all(self, request):
        Notification.objects.filter(user=request.user).delete()
        return Response({"status": "all notifications cleared"})


# =====================================================================
#                          PUSH TOKEN VIEWSET
# =====================================================================

@extend_schema_view(
    retrieve=extend_schema(
        parameters=[OpenApiParameter("id", {"type": "string", "format": "uuid"}, "path")]
    ),
    update=extend_schema(
        parameters=[OpenApiParameter("id", {"type": "string", "format": "uuid"}, "path")]
    ),
    partial_update=extend_schema(
        parameters=[OpenApiParameter("id", {"type": "string", "format": "uuid"}, "path")]
    ),
    destroy=extend_schema(
        parameters=[OpenApiParameter("id", {"type": "string", "format": "uuid"}, "path")]
    ),
)
class PushTokenViewSet(viewsets.ModelViewSet):
    """Manage push notification tokens for logged-in users."""

    serializer_class = PushTokenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PushToken.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


