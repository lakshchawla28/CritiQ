from django.urls import path
from .views import (
    CreateMatchingSessionView, JoinSessionView,
    SwipeMovieView, GetMatchResultsView, SessionDetailView
)

urlpatterns = [
    path('create/', CreateMatchingSessionView.as_view(), name='create-session'),
    path('<uuid:session_id>/join/', JoinSessionView.as_view(), name='join-session'),
    path('<uuid:session_id>/swipe/', SwipeMovieView.as_view(), name='swipe-movie'),
    path('<uuid:session_id>/results/', GetMatchResultsView.as_view(), name='match-results'),
    path('<uuid:session_id>/', SessionDetailView.as_view(), name='session-detail'),
]

