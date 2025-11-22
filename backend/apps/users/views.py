from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.utils import timezone

from apps.authentication.models import User
from .models import UserStats, UserActivity, UserPreference, BlockedUser, ReportedUser
from .serializers import (
    UserStatsSerializer, UserActivitySerializer, UserPreferenceSerializer,
    BlockedUserSerializer, ReportUserSerializer, ReportedUserSerializer,
    PublicUserProfileSerializer
)


class UserStatsView(generics.RetrieveAPIView):
    """Get user statistics"""
    serializer_class = UserStatsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        user_id = self.kwargs.get('user_id')
        
        if user_id:
            user = User.objects.get(id=user_id)
        else:
            user = self.request.user
        
        stats, created = UserStats.objects.get_or_create(user=user)
        
        if created:
            self._calculate_stats(stats)
        
        return stats
    
    def _calculate_stats(self, stats):
        """Calculate user statistics"""
        from apps.movies.models import UserMovieInteraction
        from apps.reviews.models import Review, ReviewLike
        from collections import Counter
        import datetime
        
        user = stats.user
        
        # Most watched genre
        interactions = UserMovieInteraction.objects.filter(
            user=user,
            is_watched=True
        ).select_related('movie')
        
        genres = []
        for interaction in interactions:
            genres.extend(interaction.movie.genres)
        
        if genres:
            genre_counts = Counter(genres)
            stats.most_watched_genre = dict(genre_counts.most_common(5))
        
        # Total likes received
        likes_received = ReviewLike.objects.filter(
            review__user=user
        ).count()
        stats.total_likes_received = likes_received
        
        # Watch streak
        if interactions.exists():
            last_watch = interactions.order_by('-watched_date').first()
            if last_watch and last_watch.watched_date:
                days_since = (timezone.now().date() - last_watch.watched_date.date()).days
                
                if days_since == 0:
                    stats.current_watch_streak += 1
                elif days_since == 1:
                    stats.current_watch_streak += 1
                else:
                    stats.current_watch_streak = 0
                
                stats.last_watch_date = last_watch.watched_date.date()
        
        if stats.current_watch_streak > stats.longest_watch_streak:
            stats.longest_watch_streak = stats.current_watch_streak
        
        stats.save()


class UserActivityListView(generics.ListAPIView):
    """Get user activity feed"""
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        
        if user_id:
            user = User.objects.get(id=user_id)
        else:
            user = self.request.user
        
        return UserActivity.objects.filter(user=user).order_by('-created_at')[:50]


class UserPreferencesView(generics.RetrieveUpdateAPIView):
    """Get and update user preferences"""
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        preference, created = UserPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference


class BlockUserView(APIView):
    """Block a user"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        try:
            user_to_block = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if user_to_block == request.user:
            return Response(
                {'error': 'Cannot block yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        
        blocked, created = BlockedUser.objects.get_or_create(
            user=request.user,
            blocked_user=user_to_block,
            defaults={'reason': reason}
        )
        
        if not created:
            return Response(
                {'error': 'User already blocked'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove any follow relationships
        from apps.authentication.models import UserFollow
        UserFollow.objects.filter(
            Q(follower=request.user, following=user_to_block) |
            Q(follower=user_to_block, following=request.user)
        ).delete()
        
        return Response({
            'message': 'User blocked successfully',
            'blocked': BlockedUserSerializer(blocked).data
        })


class UnblockUserView(APIView):
    """Unblock a user"""
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, user_id):
        try:
            blocked = BlockedUser.objects.get(
                user=request.user,
                blocked_user_id=user_id
            )
        except BlockedUser.DoesNotExist:
            return Response(
                {'error': 'User is not blocked'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        blocked.delete()
        
        return Response({
            'message': 'User unblocked successfully'
        })


class BlockedUsersListView(generics.ListAPIView):
    """Get list of blocked users"""
    serializer_class = BlockedUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return BlockedUser.objects.filter(
            user=self.request.user
        ).select_related('blocked_user')


class ReportUserView(APIView):
    """Report a user"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        try:
            reported_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if reported_user == request.user:
            return Response(
                {'error': 'Cannot report yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReportUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        report = ReportedUser.objects.create(
            reporter=request.user,
            reported_user=reported_user,
            reason=serializer.validated_data['reason'],
            description=serializer.validated_data['description']
        )
        
        return Response({
            'message': 'User reported successfully',
            'report_id': str(report.id)
        }, status=status.HTTP_201_CREATED)


class SearchUsersView(APIView):
    """Search for users"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        
        if not query or len(query) < 2:
            return Response(
                {'error': 'Search query must be at least 2 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Search by username, full_name
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(full_name__icontains=query)
        ).filter(is_active=True, is_verified=True)[:20]
        
        return Response({
            'query': query,
            'results': PublicUserProfileSerializer(
                users,
                many=True,
                context={'request': request}
            ).data
        })


class TopUsersView(APIView):
    """Get top users by various metrics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        metric = request.query_params.get('metric', 'movies_watched')
        limit = int(request.query_params.get('limit', 20))
        
        if metric == 'movies_watched':
            users = User.objects.filter(
                is_active=True,
                is_verified=True
            ).order_by('-movies_watched_count')[:limit]
        elif metric == 'reviews':
            users = User.objects.filter(
                is_active=True,
                is_verified=True
            ).order_by('-reviews_count')[:limit]
        elif metric == 'followers':
            users = User.objects.filter(
                is_active=True,
                is_verified=True
            ).order_by('-followers_count')[:limit]
        else:
            return Response(
                {'error': 'Invalid metric. Use: movies_watched, reviews, or followers'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'metric': metric,
            'users': PublicUserProfileSerializer(
                users,
                many=True,
                context={'request': request}
            ).data
        })