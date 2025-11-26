from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
)

from apps.authentication.models import User
from .models import UserStats, UserActivity, UserPreference, BlockedUser, ReportedUser
from .serializers import (
    UserStatsSerializer, UserActivitySerializer, UserPreferenceSerializer,
    BlockedUserSerializer, ReportUserSerializer, ReportedUserSerializer,
    PublicUserProfileSerializer, EmptySerializer, BlockUserRequestSerializer
)


# ====================================================================
# USER STATS
# ====================================================================
@extend_schema_view(
    get=extend_schema(
        summary="Get user stats",
        parameters=[
            OpenApiParameter(
                name="user_id",
                required=False,
                type=str,
                location="path",
                description="UUID of user (optional for self)"
            )
        ],
        responses=UserStatsSerializer
    )
)
class UserStatsView(generics.RetrieveAPIView):
    serializer_class = UserStatsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        user = (
            get_object_or_404(User, id=user_id)
            if user_id else self.request.user
        )
        stats, _ = UserStats.objects.get_or_create(user=user)
        return stats


# ====================================================================
# USER ACTIVITY FEED
# ====================================================================
@extend_schema_view(
    get=extend_schema(
        summary="Get activity feed",
        parameters=[
            OpenApiParameter(
                name="user_id",
                required=False,
                type=str,
                location="path",
                description="UUID of user (optional)"
            )
        ],
        responses=UserActivitySerializer
    )
)
class UserActivityListView(generics.ListAPIView):
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user = (
            get_object_or_404(User, id=user_id)
            if user_id else self.request.user
        )
        return UserActivity.objects.filter(user=user).order_by('-created_at')[:50]


# ====================================================================
# USER PREFERENCES
# ====================================================================
class UserPreferencesView(generics.RetrieveUpdateAPIView):
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        pref, _ = UserPreference.objects.get_or_create(user=self.request.user)
        return pref


# ====================================================================
# BLOCK USER
# ====================================================================
class BlockUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Block a user",
        request=BlockUserRequestSerializer,
        responses={200: BlockedUserSerializer}
    )
    def post(self, request, user_id):
        to_block = get_object_or_404(User, id=user_id)

        if to_block == request.user:
            return Response({'error': 'Cannot block yourself'}, status=400)

        serializer = BlockUserRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        blocked, created = BlockedUser.objects.get_or_create(
            user=request.user,
            blocked_user=to_block,
            defaults={'reason': serializer.validated_data.get('reason', '')}
        )

        if not created:
            return Response({'error': 'User already blocked'}, status=400)

        # remove following relations
        from apps.authentication.models import UserFollow
        UserFollow.objects.filter(
            Q(follower=request.user, following=to_block) |
            Q(follower=to_block, following=request.user)
        ).delete()

        return Response(BlockedUserSerializer(blocked).data, status=200)


# ====================================================================
# UNBLOCK USER
# ====================================================================
class UnblockUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Unblock a user",
        responses={200: OpenApiResponse(description="User unblocked")}
    )
    def delete(self, request, user_id):
        try:
            blocked = BlockedUser.objects.get(user=request.user, blocked_user_id=user_id)
        except BlockedUser.DoesNotExist:
            return Response({'error': 'User not blocked'}, status=404)

        blocked.delete()
        return Response({'message': 'User unblocked'}, status=200)


# ====================================================================
# BLOCKED USER LIST
# ====================================================================
class BlockedUsersListView(generics.ListAPIView):
    serializer_class = BlockedUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BlockedUser.objects.filter(user=self.request.user).select_related('blocked_user')


# ====================================================================
# REPORT USER
# ====================================================================
class ReportUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=ReportUserSerializer,
        responses={201: ReportedUserSerializer}
    )
    def post(self, request, user_id):
        target = get_object_or_404(User, id=user_id)

        if target == request.user:
            return Response({'error': 'Cannot report yourself'}, status=400)

        serializer = ReportUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report = ReportedUser.objects.create(
            reporter=request.user,
            reported_user=target,
            **serializer.validated_data
        )
        return Response(ReportedUserSerializer(report).data, status=201)


# ====================================================================
# SEARCH USERS
# ====================================================================
@extend_schema(
    summary="Search users",
    parameters=[
        OpenApiParameter(
            name='q',
            description="Search query (min 2 chars)",
            required=True,
            type=str,
            location='query'
        )
    ],
    responses={200: PublicUserProfileSerializer(many=True)}
)
class SearchUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        q = request.query_params.get('q', '')
        if len(q) < 2:
            return Response({'error': 'Query must be >= 2 chars'}, status=400)

        users = User.objects.filter(
            Q(username__icontains=q) | Q(full_name__icontains=q),
            is_active=True,
            is_verified=True
        )[:20]

        data = PublicUserProfileSerializer(users, many=True, context={'request': request}).data
        return Response({'query': q, 'results': data}, status=200)


# ====================================================================
# TOP USERS
# ====================================================================
@extend_schema(
    summary="Top users",
    parameters=[
        OpenApiParameter(name='metric', type=str, description="movies_watched | reviews | followers"),
        OpenApiParameter(name='limit', type=int, description="Number of users to return")
    ],
    responses={200: PublicUserProfileSerializer(many=True)}
)
class TopUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        metric = request.query_params.get('metric', 'movies_watched')
        limit = int(request.query_params.get('limit', 20))

        qs = User.objects.filter(is_active=True, is_verified=True)

        if metric == "movies_watched":
            users = qs.order_by("-movies_watched_count")[:limit]
        elif metric == "reviews":
            users = qs.order_by("-reviews_count")[:limit]
        elif metric == "followers":
            users = qs.order_by("-followers_count")[:limit]
        else:
            return Response({'error': 'Invalid metric'}, status=400)

        data = PublicUserProfileSerializer(users, many=True, context={'request': request}).data
        return Response({'metric': metric, 'users': data}, status=200)

