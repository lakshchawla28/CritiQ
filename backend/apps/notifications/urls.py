from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, PushTokenViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'push-tokens', PushTokenViewSet, basename='push-token')

urlpatterns = [
    path('', include(router.urls)),
]