from django.urls import path
from .views import (
    CreateReviewView, ReviewDetailView, LikeReviewView,
    CommentOnReviewView, RepostReviewView, UserReviewsView
)

urlpatterns = [
    path('create/', CreateReviewView.as_view(), name='create-review'),
    path('<uuid:review_id>/', ReviewDetailView.as_view(), name='review-detail'),
    path('<uuid:review_id>/like/', LikeReviewView.as_view(), name='like-review'),
    path('<uuid:review_id>/comment/', CommentOnReviewView.as_view(), name='comment-review'),
    path('<uuid:review_id>/repost/', RepostReviewView.as_view(), name='repost-review'),
    path('user/<uuid:user_id>/', UserReviewsView.as_view(), name='user-reviews'),
]