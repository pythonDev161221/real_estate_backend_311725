from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='user_register'),
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('logout/', views.logout_user, name='user_logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile management
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/extended/', views.UserExtendedProfileView.as_view(), name='user_extended_profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # Password reset
    path('password-reset/', views.request_password_reset, name='password_reset'),
    path('verify-email/', views.verify_email, name='verify_email'),
    
    # Favorite properties
    path('favorites/', views.FavoritePropertyListView.as_view(), name='favorite_properties'),
    path('favorites/<int:pk>/', views.FavoritePropertyDetailView.as_view(), name='favorite_property_detail'),
    
    # Public user information
    path('users/<int:id>/', views.PublicUserDetailView.as_view(), name='public_user_detail'),
]