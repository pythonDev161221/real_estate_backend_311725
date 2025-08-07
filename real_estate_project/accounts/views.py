from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings

from .models import User, UserProfile, FavoriteProperty
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, ChangePasswordSerializer, UserExtendedProfileSerializer,
    FavoritePropertySerializer, PublicUserSerializer
)

class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user account
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)

class UserLoginView(TokenObtainPairView):
    """
    Login user and return JWT tokens
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserProfileUpdateSerializer
        return UserProfileSerializer

class ChangePasswordView(generics.GenericAPIView):
    """
    Change user password
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)

class UserExtendedProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update extended user profile
    """
    serializer_class = UserExtendedProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

class FavoritePropertyListView(generics.ListCreateAPIView):
    """
    List and add favorite properties
    """
    serializer_class = FavoritePropertySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FavoriteProperty.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # TODO: Fetch property details from MongoDB to cache title and price
        serializer.save(user=self.request.user)

class FavoritePropertyDetailView(generics.DestroyAPIView):
    """
    Remove favorite property
    """
    serializer_class = FavoritePropertySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FavoriteProperty.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def request_password_reset(request):
    """
    Request password reset email
    """
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        # TODO: Implement password reset token generation and email sending
        # For now, just return success
        return Response({
            'message': 'Password reset email sent successfully'
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        # Don't reveal if email exists for security
        return Response({
            'message': 'Password reset email sent successfully'
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def verify_email(request):
    """
    Verify user email with token
    """
    token = request.GET.get('token')
    if not token:
        return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # TODO: Implement email verification token validation
    return Response({
        'message': 'Email verified successfully'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_user(request):
    """
    Logout user (blacklist refresh token)
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)

class PublicUserDetailView(generics.RetrieveAPIView):
    """
    Get public user information (for property listings)
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = PublicUserSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
