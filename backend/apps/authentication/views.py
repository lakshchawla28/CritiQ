from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import random

from .models import User, OTPVerification, FollowRequest, UserFollow, ChatRequest
from .serializers import (
    UserRegistrationSerializer, OTPVerifySerializer, LoginSerializer,
    UserProfileSerializer, UsernameSetSerializer
)
from utils.otp_service import send_otp


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate and send OTP
            otp_code = str(random.randint(100000, 999999))
            OTPVerification.objects.create(
                user=user,
                phone_number=user.phone_number,
                email=user.email,
                otp_code=otp_code,
                verification_type='registration',
                expires_at=timezone.now() + timedelta(minutes=10)
            )
            
            # Send OTP via SMS
            send_otp(user.phone_number, otp_code)
            
            return Response({
                'message': 'Registration successful. OTP sent to your phone.',
                'user_id': str(user.id),
                'phone_number': user.phone_number
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            otp = serializer.validated_data['otp_instance']
            otp.is_verified = True
            otp.save()
            
            # Mark user as verified
            user = otp.user
            if otp.verification_type == 'registration':
                user.phone_verified = True
                user.is_verified = True
            user.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Verification successful',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            identifier = serializer.validated_data['identifier']
            password = serializer.validated_data['password']
            
            # Try to find user by email, phone, or username
            user = None
            if '@' in identifier:
                user = User.objects.filter(email=identifier).first()
            elif identifier.isdigit():
                user = User.objects.filter(phone_number=identifier).first()
            else:
                user = User.objects.filter(username=identifier).first()
            
            if user and user.check_password(password):
                if not user.is_verified:
                    return Response({
                        'error': 'Account not verified. Please verify your phone number.'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                user.last_login = timezone.now()
                user.save()
                
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserProfileSerializer(user).data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetUsernameView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.username:
            return Response({
                'error': 'Username already set'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UsernameSetSerializer(data=request.data)
        if serializer.is_valid():
            request.user.username = serializer.validated_data['username']
            request.user.save()
            
            return Response({
                'message': 'Username set successfully',
                'user': UserProfileSerializer(request.user).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    lookup_field = 'username'


class SendFollowRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        try:
            to_user = User.objects.get(id=user_id)
            
            if to_user == request.user:
                return Response({'error': 'Cannot follow yourself'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Check if already following
            if UserFollow.objects.filter(follower=request.user, following=to_user).exists():
                return Response({'error': 'Already following'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Create or update follow request
            follow_req, created = FollowRequest.objects.get_or_create(
                from_user=request.user,
                to_user=to_user,
                defaults={'status': 'pending'}
            )
            
            if not created and follow_req.status == 'rejected':
                follow_req.status = 'pending'
                follow_req.save()
            
            return Response({
                'message': 'Follow request sent',
                'request_id': str(follow_req.id)
            }, status=status.HTTP_201_CREATED)
        
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, 
                          status=status.HTTP_404_NOT_FOUND)


class AcceptFollowRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, request_id):
        try:
            follow_req = FollowRequest.objects.get(
                id=request_id,
                to_user=request.user,
                status='pending'
            )
            
            follow_req.status = 'accepted'
            follow_req.save()
            
            # Create follow relationship
            UserFollow.objects.create(
                follower=follow_req.from_user,
                following=request.user
            )
            
            # Update counts
            follow_req.from_user.following_count += 1
            follow_req.from_user.save()
            request.user.followers_count += 1
            request.user.save()
            
            return Response({
                'message': 'Follow request accepted'
            }, status=status.HTTP_200_OK)
        
        except FollowRequest.DoesNotExist:
            return Response({'error': 'Request not found'}, 
                          status=status.HTTP_404_NOT_FOUND)


class SendChatRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        try:
            to_user = User.objects.get(id=user_id)
            message = request.data.get('message', '')
            
            if to_user == request.user:
                return Response({'error': 'Cannot chat with yourself'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            chat_req, created = ChatRequest.objects.get_or_create(
                from_user=request.user,
                to_user=to_user,
                defaults={'status': 'pending', 'message': message}
            )
            
            return Response({
                'message': 'Chat request sent',
                'request_id': str(chat_req.id)
            }, status=status.HTTP_201_CREATED)
        
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, 
                          status=status.HTTP_404_NOT_FOUND)