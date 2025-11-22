from django.test import TestCase
from rest_framework.test import APIClient
from apps.authentication.models import User

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_user_registration(self):
        data = {
            'email': 'test@example.com',
            'phone_number': '+1234567890',
            'password': 'TestPass123!',
            'full_name': 'Test User'
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
    
    def test_duplicate_email_registration(self):
        User.objects.create_user(
            email='test@example.com',
            phone_number='+1234567890',
            password='TestPass123!'
        )
        data = {
            'email': 'test@example.com',
            'phone_number': '+0987654321',
            'password': 'TestPass123!'
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, 400)