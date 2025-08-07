from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile, FavoriteProperty

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'user_type',
            'location', 'company_name', 'license_number', 'website'
        ]
        extra_kwargs = {
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Password and confirm password do not match.")
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create extended profile
        UserProfile.objects.create(user=user)
        
        return user

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError('Must include email and password.')

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    is_agent = serializers.BooleanField(read_only=True)
    is_seller = serializers.BooleanField(read_only=True)
    can_post_properties = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone', 'user_type', 'avatar', 'bio', 'location',
            'is_verified', 'is_phone_verified', 'is_email_verified',
            'company_name', 'license_number', 'website',
            'preferred_contact', 'show_contact_info', 'receive_marketing',
            'is_agent', 'is_seller', 'can_post_properties',
            'created_at', 'updated_at', 'last_login'
        ]
        read_only_fields = ['id', 'email', 'is_verified', 'is_phone_verified', 'is_email_verified', 'created_at', 'updated_at']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'user_type',
            'avatar', 'bio', 'location', 'company_name', 'license_number',
            'website', 'preferred_contact', 'show_contact_info', 'receive_marketing'
        ]
    
    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("This phone number is already in use.")
        return value

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password
    """
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New password and confirm password do not match.")
        return attrs

class UserExtendedProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for extended user profile (UserProfile model)
    """
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'user', 'preferences', 'social_links', 'saved_searches',
            'properties_posted', 'properties_sold', 'inquiries_received',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['properties_posted', 'properties_sold', 'inquiries_received', 'created_at', 'updated_at']

class FavoritePropertySerializer(serializers.ModelSerializer):
    """
    Serializer for favorite properties
    """
    class Meta:
        model = FavoriteProperty
        fields = ['id', 'property_id', 'property_title', 'property_price', 'added_at']
        read_only_fields = ['id', 'added_at']

class PublicUserSerializer(serializers.ModelSerializer):
    """
    Public serializer for user information (for property listings, etc.)
    Only shows public information based on privacy settings
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    contact_info = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'full_name', 'user_type', 'avatar',
            'bio', 'location', 'company_name', 'website', 'contact_info',
            'is_verified'
        ]
    
    def get_contact_info(self, obj):
        if not obj.show_contact_info:
            return None
        
        contact = {}
        if obj.email:
            contact['email'] = obj.email
        if obj.phone:
            contact['phone'] = obj.phone
        if obj.preferred_contact:
            contact['preferred'] = obj.preferred_contact
        
        return contact if contact else None