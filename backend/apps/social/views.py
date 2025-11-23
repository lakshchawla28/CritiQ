from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.social.models import Post, Achievement, UserAchievement, YearlyStats
from apps.reviews.models import Review
from apps.authentication.models import User


# ---------------------------------------
# Serializers
# ---------------------------------------

from rest_framework import serializers


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = "__all__"


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = "__all__"


class YearlyStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = YearlyStats
        fields = "__all__"


# =============================================================
#                     SOCIAL FEED
# =============================================================

class SocialFeedView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user

        # Show posts from user + people they follow
        following_ids = user.following.values_list("following_user_id", flat=True)

        return Post.objects.filter(
            user__id__in=list(following_ids) + [user.id]
        ).order_by("-created_at")


# =============================================================
#                     USER ACHIEVEMENTS
# =============================================================

class UserAchievementsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserAchievementSerializer

    def get_queryset(self):
        return UserAchievement.objects.filter(user=self.request.user)


# =============================================================
#                     YEARLY STATS VIEW
# =============================================================

class YearlyStatsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = YearlyStatsSerializer
    lookup_field = "year"

    def get_queryset(self):
        return YearlyStats.objects.filter(user=self.request.user)


# =============================================================
#                     YEARLY WRAP (SPOTIFY LIKE)
# =============================================================

class GenerateYearlyWrapView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, year):
        user = request.user

        stats = YearlyStats.objects.filter(user=user, year=year).first()

        if not stats:
            return Response({"message": "No stats available for this year"}, status=404)

        wrap_data = {
            "year": stats.year,
            "movies_watched": stats.movies_watched,
            "total_runtime_minutes": stats.total_runtime_minutes,
            "top_genres": stats.top_genres,
            "top_rated_movies": stats.top_rated_movies,
            "reviews_written": stats.reviews_written,
            "most_used_tags": stats.most_used_tags,
            "new_followers": stats.new_followers,
            "likes_received": stats.likes_received,
            "badges_earned": stats.badges_earned,
        }

        return Response(wrap_data, status=200)
