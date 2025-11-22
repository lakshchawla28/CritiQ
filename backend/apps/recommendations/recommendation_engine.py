import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
import pandas as pd

from apps.movies.models import Movie, UserMovieInteraction
from apps.authentication.models import User
from .models import UserPreference, Recommendation, SimilarityScore

class RecommendationEngine:
    
    def __init__(self, user):
        self.user = user
        self.rating_map = {'trash': 1, 'timepass': 2, 'worth': 3, 'peak': 4}
    
    def generate_recommendations(self, limit=20):
        """Generate personalized recommendations"""
        recommendations = []
        
        # 1. Collaborative Filtering
        collab_recs = self._collaborative_filtering(limit // 2)
        recommendations.extend(collab_recs)
        
        # 2. Content-Based Filtering
        content_recs = self._content_based_filtering(limit // 2)
        recommendations.extend(content_recs)
        
        # 3. Trending movies
        if len(recommendations) < limit:
            trending_recs = self._get_trending_movies(limit - len(recommendations))
            recommendations.extend(trending_recs)
        
        # Save recommendations
        self._save_recommendations(recommendations)
        
        return recommendations[:limit]
    
    def _collaborative_filtering(self, limit):
        """Recommend based on similar users"""
        # Get user's ratings
        user_ratings = UserMovieInteraction.objects.filter(
            user=self.user,
            rating__isnull=False
        ).select_related('movie')
        
        if user_ratings.count() < 5:
            return []
        
        # Find similar users
        similar_users = self._find_similar_users()
        
        # Get movies liked by similar users that current user hasn't seen
        recommendations = []
        seen_movie_ids = set(user_ratings.values_list('movie_id', flat=True))
        
        for similar_user in similar_users[:10]:
            similar_user_ratings = UserMovieInteraction.objects.filter(
                user=similar_user,
                rating__in=['worth', 'peak']
            ).exclude(movie_id__in=seen_movie_ids)[:5]
            
            for interaction in similar_user_ratings:
                recommendations.append({
                    'movie': interaction.movie,
                    'score': 0.8,
                    'reason': 'similar_users'
                })
        
        return recommendations[:limit]
    
    def _content_based_filtering(self, limit):
        """Recommend based on user's genre preferences"""
        # Get user's favorite genres
        user_ratings = UserMovieInteraction.objects.filter(
            user=self.user,
            rating__in=['worth', 'peak']
        ).select_related('movie')
        
        if not user_ratings.exists():
            return []
        
        # Count genre preferences
        genre_scores = defaultdict(int)
        for interaction in user_ratings:
            for genre_id in interaction.movie.genres:
                rating_score = self.rating_map.get(interaction.rating, 0)
                genre_scores[genre_id] += rating_score
        
        if not genre_scores:
            return []
        
        # Get top genres
        top_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        top_genre_ids = [g[0] for g in top_genres]
        
        # Find highly rated movies in those genres
        seen_movie_ids = user_ratings.values_list('movie_id', flat=True)
        
        recommended_movies = Movie.objects.filter(
            genres__overlap=top_genre_ids,
            app_rating_average__gte=3.0
        ).exclude(
            id__in=seen_movie_ids
        ).order_by('-app_rating_average')[:limit]
        
        return [{
            'movie': movie,
            'score': 0.75,
            'reason': 'genre_match'
        } for movie in recommended_movies]
    
    def _get_trending_movies(self, limit):
        """Get currently trending movies"""
        trending = Movie.objects.filter(
            app_rating_count__gte=10
        ).order_by('-app_rating_average', '-watch_count')[:limit]
        
        return [{
            'movie': movie,
            'score': 0.6,
            'reason': 'trending'
        } for movie in trending]
    
    def _find_similar_users(self):
        """Find users with similar taste"""
        # Get all users who rated similar movies
        user_movie_ratings = UserMovieInteraction.objects.filter(
            user=self.user,
            rating__isnull=False
        ).values_list('movie_id', 'rating')
        
        if not user_movie_ratings:
            return []
        
        user_movie_dict = {movie_id: self.rating_map[rating] 
                          for movie_id, rating in user_movie_ratings}
        
        # Find users who rated the same movies
        other_users = UserMovieInteraction.objects.filter(
            movie_id__in=user_movie_dict.keys(),
            rating__isnull=False
        ).exclude(user=self.user).values_list('user', flat=True).distinct()
        
        similarities = []
        for other_user_id in other_users:
            other_ratings = UserMovieInteraction.objects.filter(
                user_id=other_user_id,
                movie_id__in=user_movie_dict.keys(),
                rating__isnull=False
            ).values_list('movie_id', 'rating')
            
            other_movie_dict = {movie_id: self.rating_map[rating] 
                               for movie_id, rating in other_ratings}
            
            # Calculate similarity
            common_movies = set(user_movie_dict.keys()) & set(other_movie_dict.keys())
            if len(common_movies) >= 3:
                user_vector = [user_movie_dict[m] for m in common_movies]
                other_vector = [other_movie_dict[m] for m in common_movies]
                
                similarity = np.dot(user_vector, other_vector) / (
                    np.linalg.norm(user_vector) * np.linalg.norm(other_vector)
                )
                
                similarities.append((other_user_id, similarity))
        
        # Sort by similarity and return top users
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [User.objects.get(id=user_id) for user_id, _ in similarities[:10]]
    
    def _save_recommendations(self, recommendations):
        """Save recommendations to database"""
        for rec in recommendations:
            Recommendation.objects.update_or_create(
                user=self.user,
                movie=rec['movie'],
                defaults={
                    'score': rec['score'],
                    'reason': rec['reason']
                }
            )