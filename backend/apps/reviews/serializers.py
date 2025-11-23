from rest_framework import serializers
from apps.authentication.models import User
from apps.movies.serializers import MovieSerializer
from .models import Review, ReviewLike, ReviewComment, ReviewRepost


# ---------------------------------------------------------------
# Basic Serializers
# ---------------------------------------------------------------

class ReviewLikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ReviewLike
        fields = ["user", "created_at"]


class ReviewCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = ReviewComment
        fields = [
            "id",
            "user",
            "comment_text",
            "parent_comment",
            "replies",
            "created_at",
            "updated_at",
        ]

    def get_replies(self, obj):
        """Return nested replies."""
        replies = obj.replies.all()
        return ReviewCommentSerializer(replies, many=True).data


class ReviewRepostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ReviewRepost
        fields = ["id", "user", "comment", "created_at"]


# ---------------------------------------------------------------
# Review Serializers
# ---------------------------------------------------------------

class ReviewSerializer(serializers.ModelSerializer):
    """Full Review + nested comments + likes count only."""
    user = serializers.StringRelatedField(read_only=True)
    movie = MovieSerializer(read_only=True)

    likes = ReviewLikeSerializer(many=True, read_only=True)
    comments = ReviewCommentSerializer(many=True, read_only=True)
    reposts = ReviewRepostSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "movie",
            "rating",
            "review_text",
            "contains_spoilers",
            "tags",
            "privacy",
            "likes_count",
            "comments_count",
            "reposts_count",
            "likes",
            "comments",
            "reposts",
            "created_at",
            "updated_at",
        ]


class ReviewListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list endpoints."""
    user = serializers.StringRelatedField(read_only=True)
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "movie",
            "rating",
            "tags",
            "privacy",
            "likes_count",
            "comments_count",
            "reposts_count",
            "created_at",
        ]


class CreateReviewSerializer(serializers.ModelSerializer):
    """Serializer used for creating a review."""
    class Meta:
        model = Review
        fields = [
            "movie",
            "rating",
            "review_text",
            "contains_spoilers",
            "tags",
            "privacy"
        ]

    def validate(self, data):
        """Ensure user cannot review the same movie twice."""
        user = self.context["request"].user
        movie = data.get("movie")

        from .models import Review
        if Review.objects.filter(user=user, movie=movie).exists():
            raise serializers.ValidationError(
                "You have already reviewed this movie."
            )

        return data

    def create(self, validated_data):
        """Attach logged-in user automatically."""
        user = self.context["request"].user
        return Review.objects.create(user=user, **validated_data)


# ---------------------------------------------------------------
# Like Serializer
# ---------------------------------------------------------------

class LikeReviewSerializer(serializers.Serializer):
    """No fields needed — only validates action."""
    action = serializers.ChoiceField(choices=["like", "unlike"])


# ---------------------------------------------------------------
# Comment Serializer
# ---------------------------------------------------------------

class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewComment
        fields = ["comment_text", "parent_comment"]

    def create(self, validated_data):
        user = self.context["request"].user
        review = self.context["review"]
        return ReviewComment.objects.create(
            user=user,
            review=review,
            **validated_data
        )


# ---------------------------------------------------------------
# Repost Serializer
# ---------------------------------------------------------------

class CreateRepostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewRepost
        fields = ["comment"]

    def validate(self, data):
        """Ensure user cannot repost same review twice."""
        user = self.context["request"].user
        review = self.context["review"]

        if ReviewRepost.objects.filter(user=user, original_review=review).exists():
            raise serializers.ValidationError("You already reposted this review.")
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        review = self.context["review"]

        return ReviewRepost.objects.create(
            user=user,
            original_review=review,
            **validated_data
        )
