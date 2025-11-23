from django.urls import path
from .views import (
    CreateMatchingSessionView,
    JoinSessionView,
    SwipeMovieView,
    GetMatchResultsView,
    SessionDetailView,
)

urlpatterns = [
    # -----------------------------------
    # Create a session
    # -----------------------------------
    path("create/", CreateMatchingSessionView.as_view(), name="create-session"),

    # -----------------------------------
    # Session Actions
    # -----------------------------------
    path("<uuid:session_id>/join/", JoinSessionView.as_view(), name="join-session"),
    path("<uuid:session_id>/swipe/", SwipeMovieView.as_view(), name="swipe-movie"),
    path("<uuid:session_id>/results/", GetMatchResultsView.as_view(), name="match-results"),

    # -----------------------------------
    # Session Details (Last!)
    # -----------------------------------
    path("<uuid:session_id>/", SessionDetailView.as_view(), name="session-detail"),
]

