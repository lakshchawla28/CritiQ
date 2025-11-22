from django.test import TestCase
from rest_framework.test import APIClient
from apps.authentication.models import User
from .models import UserStats, UserPreference, BlockedUser

class UsersAppTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            phone_number='+1234567890',
            password='TestPass123!',
            username='testuser'
        )
        self.user.is_verified = True
        self.user.save()
    
    def test_user_stats_creation(self):
        """Test user stats are created automatically"""
        stats, created = UserStats.objects.get_or_create(user=self.user)
        self.assertTrue(stats is not None)
    
    def test_user_preferences_creation(self):
        """Test user preferences are created"""
        prefs, created = UserPreference.objects.get_or_create(user=self.user)
        self.assertTrue(prefs.email_notifications)
    
    def test_block_user(self):
        """Test blocking a user"""
        other_user = User.objects.create_user(
            email='other@example.com',
            phone_number='+0987654321',
            password='TestPass123!',
            username='otheruser'
        )
        
        blocked = BlockedUser.objects.create(
            user=self.user,
            blocked_user=other_user,
            reason='Test blocking'
        )
        
        self.assertEqual(blocked.user, self.user)
        self.assertEqual(blocked.blocked_user, other_user)