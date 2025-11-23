from celery import shared_task
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import datetime
from apps.authentication.models import User
from apps.movies.models import UserMovieInteraction
from apps.reviews.models import Review, ReviewLike
from .models import YearlyStats, UserAchievement


@shared_task
def generate_yearly_stats_for_all_users(year=None):
    """
    Generate yearly stats for all users.
    Run this at the end of each year or manually.
    """
    if year is None:
        year = timezone.now().year - 1  # Previous year
    
    users = User.objects.filter(is_active=True)
    
    for user in users:
        generate_yearly_stats_for_user.delay(user.id, year)
    
    return f"Yearly stats generation queued for {users.count()} users"


@shared_task
def generate_yearly_stats_for_user(user_id, year=None):
    """
    Generate yearly stats for a single user.
    """
    if year is None:
        year = timezone.now().year
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return f"User {user_id} does not exist"
    
    # Date range for the year
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31, 23, 59, 59)
    
    # Movies watched
    watched_movies = UserMovieInteraction.objects.filter(
        user=user,
        is_watched=True,
        watched_date__range=[start_date, end_date]
    ).select_related('movie')
    
    movies_watched_count = watched_movies.count()
    
    # Total runtime
    total_runtime = sum(
        movie.movie.runtime or 0 
        for movie in watched_movies 
        if movie.movie.runtime
    )
    
    # Top genres (count movies per genre)
    genre_counts = {}
    for interaction in watched_movies:
        for genre_id in interaction.movie.genres:
            genre_counts[genre_id] = genre_counts.get(genre_id, 0) + 1
    
    # Sort and get top 5 genres
    top_genres = sorted(
        genre_counts.items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:5]
    
    # Top rated movies
    top_rated = watched_movies.filter(
        rating__in=['peak', 'worth']
    ).values_list('movie__id', 'movie__title', 'rating')[:10]
    
    top_rated_movies = [
        {'movie_id': str(m[0]), 'title': m[1], 'rating': m[2]} 
        for m in top_rated
    ]
    
    # Reviews written
    reviews = Review.objects.filter(
        user=user,
        created_at__range=[start_date, end_date]
    )
    
    reviews_written_count = reviews.count()
    
    # Average rating given
    rating_map = {'trash': 1, 'timepass': 2, 'worth': 3, 'peak': 4}
    ratings = [rating_map.get(r.rating) for r in reviews if r.rating]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # Most used tags
    tag_counts = {}
    for review in reviews:
        for tag in review.tags.all():
            tag_counts[tag.name] = tag_counts.get(tag.name, 0) + 1
    
    most_used_tags = sorted(
        tag_counts.items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:10]
    
    # Social stats
    followers_start = user.followers.filter(
        created_at__lt=start_date
    ).count()
    followers_end = user.followers.filter(
        created_at__lte=end_date
    ).count()
    new_followers = followers_end - followers_start
    
    # Likes received
    likes_received = ReviewLike.objects.filter(
        review__user=user,
        created_at__range=[start_date, end_date]
    ).count()
    
    # Badges earned
    badges = UserAchievement.objects.filter(
        user=user,
        earned_at__range=[start_date, end_date]
    ).select_related('achievement')
    
    badges_earned = [
        {
            'name': badge.achievement.name,
            'icon': badge.achievement.icon,
            'earned_at': badge.earned_at.isoformat()
        }
        for badge in badges
    ]
    
    # Create or update yearly stats
    yearly_stats, created = YearlyStats.objects.update_or_create(
        user=user,
        year=year,
        defaults={
            'movies_watched': movies_watched_count,
            'total_runtime_minutes': total_runtime,
            'top_genres': [{'genre_id': g[0], 'count': g[1]} for g in top_genres],
            'top_rated_movies': top_rated_movies,
            'reviews_written': reviews_written_count,
            'avg_rating_given': round(avg_rating, 2),
            'most_used_tags': [{'tag': t[0], 'count': t[1]} for t in most_used_tags],
            'new_followers': new_followers,
            'likes_received': likes_received,
            'badges_earned': badges_earned,
        }
    )
    
    return f"Yearly stats {'created' if created else 'updated'} for {user.username} ({year})"