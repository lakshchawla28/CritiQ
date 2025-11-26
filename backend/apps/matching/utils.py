"""
Utility functions for matching logic.
"""
from django.db import transaction
from django.utils import timezone
from .models import MatchingSession, MovieSwipe, MatchResult
from apps.movies.models import Movie


def calculate_match_results_for_session(session: MatchingSession):
    """
    Recalculate MatchResult objects for the session.
    - Count likes per movie
    - Compute percent: (likes_count / participants_count) * 100
    - Replace MatchResult rows for the session (safe within atomic)
    Returns the list of MatchResult instances ordered by match_percentage desc.
    """
    participants_count = session.participants.count() or 1  # avoid div by zero

    # collect likes per movie
    swipes = MovieSwipe.objects.filter(session=session)
    movie_like_map = {}
    for s in swipes:
        if s.liked:
            movie_like_map.setdefault(s.movie_id, 0)
            movie_like_map[s.movie_id] += 1

    with transaction.atomic():
        # remove old results
        MatchResult.objects.filter(session=session).delete()

        results = []
        for movie_id, likes_count in movie_like_map.items():
            try:
                movie = Movie.objects.get(id=movie_id)
            except Movie.DoesNotExist:
                continue

            percent = (likes_count / participants_count) * 100.0
            mr = MatchResult.objects.create(
                session=session,
                movie=movie,
                likes_count=likes_count,
                match_percentage=round(percent, 2),
                matched_at=timezone.now(),
            )
            results.append(mr)

    # return results sorted
    results.sort(key=lambda r: (r.match_percentage, r.likes_count), reverse=True)
    return results
