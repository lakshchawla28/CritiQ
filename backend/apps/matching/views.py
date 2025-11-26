# apps/matching/views.py
"""
REST endpoints for matching sessions.
- create session
- join session
- swipe (like/pass)
- get match results
- session detail
"""
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import MatchingSession, MovieSwipe, MatchResult
from .serializers import (
    MatchingSessionCreateSerializer,
    MatchingSessionSerializer,
    MovieSwipeSerializer,
    MatchResultSerializer,
)
from apps.movies.models import Movie

from .utils import calculate_match_results_for_session  # helper implemented above


class CreateMatchingSessionView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MatchingSessionCreateSerializer

    def perform_create(self, serializer):
        session = serializer.save(created_by=self.request.user)
        session.participants.add(self.request.user)
        # do not call session.save() here again; created_by saved by serializer


class JoinSessionView(generics.GenericAPIView):
    """
    POST: join a session (no request body). Returns serialized session.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MatchingSessionSerializer  # used for response

    def post(self, request, session_id):
        session = get_object_or_404(MatchingSession, id=session_id)

        if session.status in ['completed', 'cancelled']:
            return Response({'error': 'Cannot join a finished session'}, status=status.HTTP_400_BAD_REQUEST)

        if request.user in session.participants.all():
            serializer = self.get_serializer(session, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        session.participants.add(request.user)
        session.save(update_fields=['updated_at'])
        serializer = self.get_serializer(session, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class SwipeMovieView(generics.GenericAPIView):
    """
    POST: Body: { "movie_id": "<uuid>", "liked": true/false }
    Creates or updates a MovieSwipe for the (session, user, movie).
    After each update, recompute the MatchResults.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MovieSwipeSerializer  # describes the swipe structure

    def post(self, request, session_id):
        session = get_object_or_404(MatchingSession, id=session_id)

        if request.user not in session.participants.all():
            return Response({'error': 'You must join the session first'}, status=status.HTTP_403_FORBIDDEN)

        movie_id = request.data.get('movie_id')
        liked = request.data.get('liked', True)

        if movie_id is None:
            return Response({'error': 'movie_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        movie = get_object_or_404(Movie, id=movie_id)

        # upsert swipe
        with transaction.atomic():
            swipe, created = MovieSwipe.objects.update_or_create(
                session=session, user=request.user, movie=movie,
                defaults={'liked': bool(liked)}
            )

            # recalc results (helper will delete & recreate MatchResult rows)
            results = calculate_match_results_for_session(session)

        # Return the updated swipe and results to client
        swipe_serializer = self.get_serializer(swipe, context={'request': request})
        results_serializer = MatchResultSerializer(results, many=True, context={'request': request})
        return Response({'swipe': swipe_serializer.data, 'results': results_serializer.data}, status=status.HTTP_200_OK)


class GetMatchResultsView(generics.ListAPIView):
    """
    GET: list MatchResult objects for a session (ordered).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MatchResultSerializer

    def get_queryset(self):
        session_id = self.kwargs.get('session_id')
        session = get_object_or_404(MatchingSession, id=session_id)
        return MatchResult.objects.filter(session=session).order_by('-match_percentage', '-matched_at')

    # ListAPIView already implements get() using serializer_class


class SessionDetailView(generics.GenericAPIView):
    """
    GET: detailed session info (session data, swipes count, results summary).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MatchingSessionSerializer

    def get(self, request, session_id):
        session = get_object_or_404(MatchingSession, id=session_id)
        serializer = self.get_serializer(session, context={'request': request})

        # include swipes and results summary
        swipes = MovieSwipe.objects.filter(session=session).select_related('movie', 'user')
        results = MatchResult.objects.filter(session=session).order_by('-match_percentage')

        results_data = MatchResultSerializer(results, many=True, context={'request': request}).data

        return Response({
            'session': serializer.data,
            'swipes_count': swipes.count(),
            'results': results_data,
        }, status=status.HTTP_200_OK)




