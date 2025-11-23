from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Swagger / OpenAPI
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # ===========================
    # Django Admin
    # ===========================
    path("admin/", admin.site.urls),

    # ===========================
    # API ROUTES
    # ===========================
    path("api/auth/", include("apps.authentication.urls")),
    path("api/users/", include("apps.users.urls")),
    path("api/movies/", include("apps.movies.urls")),
    path("api/reviews/", include("apps.reviews.urls")),
    path("api/social/", include("apps.social.urls")),
    path("api/chat/", include("apps.chat.urls")),
    path("api/matching/", include("apps.matching.urls")),
    path("api/recommendations/", include("apps.recommendations.urls")),

    # ===========================
    # API SCHEMA (JSON)
    # ===========================
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),

    # ===========================
    # API DOCUMENTATION
    # ===========================
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]


# ===========================
# MEDIA (Images, uploads)
# ===========================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

