from rest_framework import serializers
from apps.social.models import Post, Achievement, UserAchievement, YearlyStats
from apps.reviews.serializers import ReviewSerializer
from apps.authentication.models import User


# ------------------------------
# USER MINI
# ------------------------------
class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "profile_picture"]


# ------------------------------
# POST SERIALIZER
# ------------------------------
class PostSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    review = ReviewSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "user",
            "content",
            "review",
            "likes_count",
            "comments_count",
            "created_at",
            "updated_at",
        ]


# ------------------------------
# ACHIEVEMENTS
# ------------------------------
class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = "__all__"


class UserAchievementSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = "__all__"


# ------------------------------
# YEARLY STATS
# ------------------------------
class YearlyStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = YearlyStats
        fields = "__all__"
