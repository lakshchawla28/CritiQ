# apps/reviews/views.py
from rest_framework import status, generics, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

from .models import Review, ReviewLike, ReviewComment, ReviewRepost
from apps.authentication.models import User
from apps.movies.models import Movie

from .serializers import ReviewSerializer, ReviewCommentSerializer


# ------------------------
# Lightweight input serializers
# ------------------------
class CreateReviewInputSerializer(serializers.Serializer):
    movie_id = serializers.UUIDField()
    rating = serializers.IntegerField(min_value=0, max_value=10)
    review_text = serializers.CharField(allow_blank=True, required=False)
    contains_spoilers = serializers.BooleanField(required=False, default=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False, default=list)


class EmptySerializer(serializers.Serializer):
    pass


class CommentInputSerializer(serializers.Serializer):
    comment_text = serializers.CharField()


class RepostInputSerializer(serializers.Serializer):
    comment = serializers.CharField(allow_blank=True, required=False)


# ============================================================
#                     CREATE REVIEW
# ============================================================

class CreateReviewView(generics.CreateAPIView):
    """
    POST: create a review for a movie.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CreateReviewInputSerializer  # input shape

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        movie = get_object_or_404(Movie, id=data["movie_id"])

        # Prevent duplicate review
        if Review.objects.filter(user=request.user, movie=movie).exists():
            return Response(
                {"error": "You have already reviewed this movie"},
                status=status.HTTP_400_BAD_REQUEST
            )

        review = Review.objects.create(
            user=request.user,
            movie=movie,
            rating=data.get("rating"),
            review_text=data.get("review_text", ""),
            contains_spoilers=data.get("contains_spoilers", False),
            tags=data.get("tags", []),
        )

        # Return full review representation
        return Response(ReviewSerializer(review, context={"request": request}).data, status=status.HTTP_201_CREATED)


# ============================================================
#                  GET / DELETE REVIEW
# ============================================================

class ReviewDetailView(generics.RetrieveDestroyAPIView):
    """
    GET: retrieve review
    DELETE: delete review (owner only)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "review_id"

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != request.user:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


# ============================================================
#                         LIKE REVIEW
# ============================================================

class LikeReviewView(generics.GenericAPIView):
    """
    POST: toggle like on a review (creates or deletes ReviewLike)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer  # no body expected

    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)

        like, created = ReviewLike.objects.get_or_create(user=request.user, review=review)

        if not created:
            # User already liked → unlike
            like.delete()
            review.likes_count = max(0, review.likes_count - 1)
            review.save(update_fields=["likes_count"])
            return Response({"liked": False}, status=status.HTTP_200_OK)

        # New like
        review.likes_count = (review.likes_count or 0) + 1
        review.save(update_fields=["likes_count"])
        return Response({"liked": True}, status=status.HTTP_200_OK)


# ============================================================
#                     COMMENT ON REVIEW
# ============================================================

class CommentOnReviewView(generics.GenericAPIView):
    """
    POST: add a comment to a review
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CommentInputSerializer

    def post(self, request, review_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review = get_object_or_404(Review, id=review_id)

        comment = ReviewComment.objects.create(
            user=request.user,
            review=review,
            comment_text=serializer.validated_data["comment_text"],
        )

        review.comments_count = (review.comments_count or 0) + 1
        review.save(update_fields=["comments_count"])

        return Response(ReviewCommentSerializer(comment, context={"request": request}).data, status=status.HTTP_201_CREATED)


# ============================================================
#                        REPOST REVIEW
# ============================================================

class RepostReviewView(generics.GenericAPIView):
    """
    POST: repost (share) an existing review with optional comment (toggle behavior)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RepostInputSerializer

    def post(self, request, review_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        original_review = get_object_or_404(Review, id=review_id)
        comment = serializer.validated_data.get("comment", "")

        repost, created = ReviewRepost.objects.get_or_create(
            user=request.user,
            original_review=original_review,
            defaults={"comment": comment}
        )

        if not created:
            # User already reposted → remove repost
            repost.delete()
            original_review.reposts_count = max(0, original_review.reposts_count - 1)
            original_review.save(update_fields=["reposts_count"])
            return Response({"reposted": False}, status=status.HTTP_200_OK)

        original_review.reposts_count = (original_review.reposts_count or 0) + 1
        original_review.save(update_fields=["reposts_count"])
        return Response({"reposted": True}, status=status.HTTP_201_CREATED)


# ============================================================
#                LIST ALL REVIEWS OF A USER
# ============================================================

class UserReviewsView(generics.ListAPIView):
    """
    GET: list all reviews made by a user
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        user = get_object_or_404(User, id=user_id)
        return Review.objects.filter(user=user).order_by("-created_at")

