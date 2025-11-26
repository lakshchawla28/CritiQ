from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import Review, ReviewLike, ReviewComment, ReviewRepost
from apps.movies.serializers import MovieSerializer


# =====================================================================
#                          LIKE SERIALIZER
# =====================================================================

class ReviewLikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ReviewLike
        fields = ["user", "created_at"]


# =====================================================================
#                          COMMENT SERIALIZER
# =====================================================================

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

    @extend_schema_field(serializers.ListSerializer(child=serializers.DictField()))
    def get_replies(self, obj):
        queryset = obj.replies.all()
        return ReviewCommentSerializer(queryset, many=True).data


# =====================================================================
#                          REPOST SERIALIZER
# =====================================================================

class ReviewRepostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ReviewRepost
        fields = ["id", "user", "comment", "created_at"]


# =====================================================================
#                          FULL REVIEW SERIALIZER
# =====================================================================

class ReviewSerializer(serializers.ModelSerializer):
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


# =====================================================================
#                          LIGHTWEIGHT LIST SERIALIZER
# =====================================================================

class ReviewListSerializer(serializers.ModelSerializer):
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


# =====================================================================
#                          CREATE REVIEW
# =====================================================================

class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "movie",
            "rating",
            "review_text",
            "contains_spoilers",
            "tags",
            "privacy",
        ]

    def validate(self, data):
        user = self.context["request"].user
        movie = data["movie"]

        if Review.objects.filter(user=user, movie=movie).exists():
            raise serializers.ValidationError("You have already reviewed this movie.")

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        return Review.objects.create(user=user, **validated_data)


# =====================================================================
#                          COMMENT CREATION
# =====================================================================

class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewComment
        fields = ["comment_text", "parent_comment"]

    def create(self, validated_data):
        user = self.context["request"].user
        review = self.context["review"]
        return ReviewComment.objects.create(user=user, review=review, **validated_data)


# =====================================================================
#                          REPOST CREATION
# =====================================================================

class CreateRepostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewRepost
        fields = ["comment"]

    def validate(self, data):
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


