from django.urls import path
from .views import (
    SearchMoviesView, MovieDetailView, PopularMoviesView,
    UpcomingMoviesView, MarkMovieWatchedView, RateMovieView,
    MarkInterestedView, UserWatchlistView, CreateWatchlistView
)

urlpatterns = [
    path('search/', SearchMoviesView.as_view(), name='search-movies'),
    path('<uuid:movie_id>/', MovieDetailView.as_view(), name='movie-detail'),
    path('popular/', PopularMoviesView.as_view(), name='popular-movies'),
    path('upcoming/', UpcomingMoviesView.as_view(), name='upcoming-movies'),
    path('<uuid:movie_id>/watched/', MarkMovieWatchedView.as_view(), name='mark-watched'),
    path('<uuid:movie_id>/rate/', RateMovieView.as_view(), name='rate-movie'),
    path('<uuid:movie_id>/interested/', MarkInterestedView.as_view(), name='mark-interested'),
    path('watchlists/', UserWatchlistView.as_view(), name='user-watchlists'),
    path('watchlists/create/', CreateWatchlistView.as_view(), name='create-watchlist'),
]

