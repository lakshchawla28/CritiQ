from rest_framework import status, generics, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, OpenApiResponse
import random

from django.shortcuts import get_object_or_404

from .models import User, OTPVerification, FollowRequest, UserFollow, ChatRequest
from .serializers import (
    UserRegistrationSerializer, OTPVerifySerializer, LoginSerializer,
    UserProfileSerializer, UsernameSetSerializer, LoginResponseSerializer,
    FollowRequestSerializer, ChatRequestSerializer, EmptySerializer,
    SendChatRequestCreateSerializer
)
from utils.otp_service import send_otp


class RegisterView(APIView):
    """
    User Registration Endpoint

    Register a new user with email, phone number, and password.
    An OTP will be sent to the provided phone number for verification.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(
                description="Registration successful",
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'},
                        'user_id': {'type': 'string'},
                        'phone_number': {'type': 'string'}
                    }
                }
            ),
            400: OpenApiResponse(description="Bad request - validation errors")
        },
        tags=['Authentication'],
    )
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
    """
    OTP Verification Endpoint
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = OTPVerifySerializer

    @extend_schema(
        request=OTPVerifySerializer,
        responses={
            200: LoginResponseSerializer,
            400: OpenApiResponse(description="Invalid or expired OTP")
        },
        tags=['Authentication'],
    )
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            otp = serializer.validated_data['otp_instance']
            otp.is_verified = True
            otp.save(update_fields=['is_verified'])

            # Mark user as verified
            user = otp.user
            if otp.verification_type == 'registration':
                user.phone_verified = True
                user.is_verified = True
                user.save(update_fields=['phone_verified', 'is_verified'])

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Verification successful',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserProfileSerializer(user, context={'request': request}).data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    User Login Endpoint
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: LoginResponseSerializer,
            401: OpenApiResponse(description="Invalid credentials"),
            403: OpenApiResponse(description="Account not verified")
        },
        tags=['Authentication'],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            identifier = serializer.validated_data['identifier']
            password = serializer.validated_data['password']

            # Try to find user by email, phone, or username
            user = None
            if '@' in identifier:
                user = User.objects.filter(email=identifier).first()
            elif identifier.startswith('+') or identifier.isdigit():
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
                user.save(update_fields=['last_login'])

                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserProfileSerializer(user, context={'request': request}).data
                }, status=status.HTTP_200_OK)

            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):
    """
    Refresh JWT Token Endpoint
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request={
            'type': 'object',
            'properties': {
                'refresh': {'type': 'string'}
            }
        },
        responses={
            200: OpenApiResponse(
                description="New access token",
                response={
                    'type': 'object',
                    'properties': {
                        'access': {'type': 'string'}
                    }
                }
            )
        },
        tags=['Authentication'],
    )
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token required'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Invalid refresh token'},
                            status=status.HTTP_401_UNAUTHORIZED)


class SetUsernameView(APIView):
    """
    Set Username Endpoint
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=UsernameSetSerializer,
        responses={
            200: UserProfileSerializer,
            400: OpenApiResponse(description="Username already set or invalid")
        },
        tags=['Authentication'],
    )
    def post(self, request):
        if request.user.username:
            return Response({
                'error': 'Username already set'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = UsernameSetSerializer(data=request.data)
        if serializer.is_valid():
            request.user.username = serializer.validated_data['username']
            request.user.save(update_fields=['username'])

            return Response({
                'message': 'Username set successfully',
                'user': UserProfileSerializer(request.user, context={'request': request}).data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    User Profile Endpoint
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Authentication'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Authentication'])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(tags=['Authentication'])
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class UserDetailView(generics.RetrieveAPIView):
    """
    User Detail Endpoint
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    lookup_field = 'username'

    @extend_schema(tags=['Users'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# -----------------------------
# Follow / Accept follow
# -----------------------------
class SendFollowRequestView(generics.GenericAPIView):
    """
    Send a follow request to another user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmptySerializer  # no body expected

    @extend_schema(
        request=EmptySerializer,
        responses={
            201: OpenApiResponse(description="Follow request sent", response=FollowRequestSerializer),
            400: OpenApiResponse(description="Bad request"),
            404: OpenApiResponse(description="User not found")
        },
        tags=['Authentication'],
    )
    def post(self, request, user_id):
        to_user = get_object_or_404(User, id=user_id)

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
            follow_req.save(update_fields=['status'])

        return Response({
            'message': 'Follow request sent',
            'request_id': str(follow_req.id)
        }, status=status.HTTP_201_CREATED)


class AcceptFollowRequestView(generics.GenericAPIView):
    """
    Accept a pending follow request.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmptySerializer

    @extend_schema(
        request=EmptySerializer,
        responses={
            200: OpenApiResponse(description="Follow request accepted"),
            404: OpenApiResponse(description="Request not found")
        },
        tags=['Authentication'],
    )
    def post(self, request, request_id):
        follow_req = get_object_or_404(FollowRequest, id=request_id, to_user=request.user, status='pending')

        follow_req.status = 'accepted'
        follow_req.save(update_fields=['status'])

        # Create follow relationship
        UserFollow.objects.create(
            follower=follow_req.from_user,
            following=request.user
        )

        return Response({'message': 'Follow request accepted'}, status=status.HTTP_200_OK)


class SendChatRequestView(generics.GenericAPIView):
    """
    Send Chat Request Endpoint
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SendChatRequestCreateSerializer

    @extend_schema(
        request=SendChatRequestCreateSerializer,
        responses={
            201: OpenApiResponse(description="Chat request sent", response=ChatRequestSerializer),
            400: OpenApiResponse(description="Bad request"),
            404: OpenApiResponse(description="User not found")
        },
        tags=['Authentication'],
    )
    def post(self, request, user_id):
        to_user = get_object_or_404(User, id=user_id)
        serializer = SendChatRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data.get('message', '')

        if to_user == request.user:
            return Response({'error': 'Cannot chat with yourself'},
                            status=status.HTTP_400_BAD_REQUEST)

        chat_req, created = ChatRequest.objects.get_or_create(
            from_user=request.user,
            to_user=to_user,
            defaults={'status': 'pending', 'message': message}
        )

        # if existing and rejected, reopen
        if not created and chat_req.status == 'rejected':
            chat_req.status = 'pending'
            chat_req.message = message
            chat_req.save(update_fields=['status', 'message'])

        return Response({
            'message': 'Chat request sent',
            'request_id': str(chat_req.id)
        }, status=status.HTTP_201_CREATED)

# ---------------------------------------