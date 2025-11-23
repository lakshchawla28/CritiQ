from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

from .models import Review, ReviewLike, ReviewComment, ReviewRepost
from apps.authentication.models import User
from apps.movies.models import Movie

from .serializers import ReviewSerializer, ReviewCommentSerializer


# ============================================================
#                     CREATE REVIEW
# ============================================================

class CreateReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        movie_id = request.data.get("movie_id")
        rating = request.data.get("rating")
        review_text = request.data.get("review_text")
        contains_spoilers = request.data.get("contains_spoilers", False)
        tags = request.data.get("tags", [])

        movie = get_object_or_404(Movie, id=movie_id)

        # Prevent duplicate review
        if Review.objects.filter(user=request.user, movie=movie).exists():
            return Response(
                {"error": "You have already reviewed this movie"},
                status=400
            )

        review = Review.objects.create(
            user=request.user,
            movie=movie,
            rating=rating,
            review_text=review_text,
            contains_spoilers=contains_spoilers,
            tags=tags,
        )

        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


# ============================================================
#                  GET / DELETE REVIEW
# ============================================================

class ReviewDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        return Response(ReviewSerializer(review).data)

    def delete(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)

        if review.user != request.user:
            return Response({"error": "Not allowed"}, status=403)

        review.delete()
        return Response({"success": "Review deleted"})


# ============================================================
#                         LIKE REVIEW
# ============================================================

class LikeReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)

        like, created = ReviewLike.objects.get_or_create(
            user=request.user,
            review=review,
        )

        if not created:
            # User already liked → unlike
            like.delete()
            review.likes_count -= 1
            review.save(update_fields=["likes_count"])
            return Response({"liked": False})

        # New like
        review.likes_count += 1
        review.save(update_fields=["likes_count"])
        return Response({"liked": True})


# ============================================================
#                     COMMENT ON REVIEW
# ============================================================

class CommentOnReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):
        comment_text = request.data.get("comment_text")

        if not comment_text:
            return Response({"error": "comment_text required"}, status=400)

        review = get_object_or_404(Review, id=review_id)

        comment = ReviewComment.objects.create(
            user=request.user,
            review=review,
            comment_text=comment_text,
        )

        review.comments_count += 1
        review.save(update_fields=["comments_count"])

        return Response(ReviewCommentSerializer(comment).data, status=201)


# ============================================================
#                        REPOST REVIEW
# ============================================================

class RepostReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):
        original_review = get_object_or_404(Review, id=review_id)
        comment = request.data.get("comment", "")

        # Repost uses: original_review NOT "review"
        repost, created = ReviewRepost.objects.get_or_create(
            user=request.user,
            original_review=original_review,
            defaults={"comment": comment}
        )

        if not created:
            # User already reposted → remove repost
            repost.delete()
            original_review.reposts_count -= 1
            original_review.save(update_fields=["reposts_count"])
            return Response({"reposted": False})

        original_review.reposts_count += 1
        original_review.save(update_fields=["reposts_count"])

        return Response({"reposted": True})


# ============================================================
#                LIST ALL REVIEWS OF A USER
# ============================================================

class UserReviewsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        reviews = Review.objects.filter(user=user).order_by("-created_at")
        return Response(ReviewSerializer(reviews, many=True).data)
