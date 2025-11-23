from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

from .models import MatchingSession, MovieSwipe, MatchResult
from .serializers import (
    MatchingSessionSerializer,
    MatchingSessionDetailSerializer,
    MovieSwipeSerializer,
    MatchResultSerializer,
)

from apps.movies.models import Movie


# ================================================================
# Helper: Generate Match Results
# ================================================================

def calculate_match_results(session):
    """
    Matching Logic:
    - Count likes per movie
    - Higher likes = higher match score
    """
    MatchResult.objects.filter(session=session).delete()

    swipes = MovieSwipe.objects.filter(session=session)

    movie_scores = {}
    for swipe in swipes:
        if swipe.movie_id not in movie_scores:
            movie_scores[swipe.movie_id] = 0
        if swipe.liked:
            movie_scores[swipe.movie_id] += 1

    results = []
    for movie_id, score in movie_scores.items():
        movie = get_object_or_404(Movie, id=movie_id)
        result = MatchResult.objects.create(
            session=session,
            movie=movie,
            match_score=score
        )
        results.append(result)

    return sorted(results, key=lambda x: x.match_score, reverse=True)


# ================================================================
# Create Matching Session
# ================================================================

class CreateMatchingSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session = MatchingSession.objects.create(
            created_by=request.user
        )
        session.participants.add(request.user)

        return Response(
            MatchingSessionSerializer(session).data,
            status=status.HTTP_201_CREATED
        )


# ================================================================
# Join Matching Session
# ================================================================

class JoinSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session = get_object_or_404(MatchingSession, id=session_id)

        if request.user in session.participants.all():
            return Response({"message": "Already joined"}, status=200)

        session.participants.add(request.user)
        session.save()

        return Response(
            MatchingSessionSerializer(session).data,
            status=status.HTTP_200_OK
        )


# ================================================================
# Swipe Movie (Like / Dislike)
# ================================================================

class SwipeMovieView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session = get_object_or_404(MatchingSession, id=session_id)

        movie_id = request.data.get("movie_id")
        liked = request.data.get("liked")

        if movie_id is None or liked is None:
            return Response({"error": "movie_id and liked required"}, status=400)

        # Convert liked to boolean
        liked = True if str(liked).lower() in ["true", "1", "yes"] else False

        movie = get_object_or_404(Movie, id=movie_id)

        swipe, _ = MovieSwipe.objects.update_or_create(
            session=session,
            user=request.user,
            movie=movie,
            defaults={"liked": liked}
        )

        return Response(
            MovieSwipeSerializer(swipe).data,
            status=status.HTTP_200_OK
        )


# ================================================================
# Get Match Results
# ================================================================

class GetMatchResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = get_object_or_404(MatchingSession, id=session_id)

        results = calculate_match_results(session)
        serializer = MatchResultSerializer(results, many=True)

        return Response(serializer.data, status=200)


# ================================================================
# Session Detail
# ================================================================

class SessionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = get_object_or_404(MatchingSession, id=session_id)
        serializer = MatchingSessionDetailSerializer(session)
        return Response(serializer.data, status=200)

