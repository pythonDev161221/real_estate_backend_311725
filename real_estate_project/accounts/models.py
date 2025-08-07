from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    """
    Custom User model for Real Estate platform
    Extends Django's AbstractUser with real estate-specific fields
    """
    
    USER_TYPE_CHOICES = [
        ('buyer', 'Buyer/Tenant'),
        ('seller', 'Seller/Landlord'),
        ('agent', 'Real Estate Agent'),
    ]
    
    CONTACT_PREFERENCE_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('both', 'Both'),
    ]
    
    # Basic Info - Override to make email unique and required
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    
    # Phone validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # Real Estate Specific
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='buyer',
        help_text="User's role in the real estate ecosystem"
    )
    
    # Profile Information
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True, help_text="City, State")
    
    # Verification & Trust
    is_verified = models.BooleanField(
        default=False,
        help_text="User has verified their email and phone number"
    )
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    
    # Business Information (for agents and professional sellers)
    company_name = models.CharField(max_length=100, blank=True)
    license_number = models.CharField(max_length=50, blank=True, help_text="Real estate license number")
    website = models.URLField(blank=True)
    
    # Contact Preferences
    preferred_contact = models.CharField(
        max_length=10,
        choices=CONTACT_PREFERENCE_CHOICES,
        default='email'
    )
    
    # Privacy Settings
    show_contact_info = models.BooleanField(
        default=True,
        help_text="Allow other users to see contact information"
    )
    receive_marketing = models.BooleanField(
        default=True,
        help_text="Receive marketing emails and notifications"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Override username to use email for login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    
    @property
    def is_agent(self):
        return self.user_type == 'agent'
    
    @property
    def is_seller(self):
        return self.user_type in ['seller', 'agent']
    
    @property
    def can_post_properties(self):
        """Check if user can post properties"""
        return self.user_type in ['seller', 'agent'] and self.is_verified

class UserProfile(models.Model):
    """
    Extended profile information stored in MongoDB-like format
    This allows for flexible profile data without database migrations
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_extended')
    
    # JSON field for flexible profile data
    preferences = models.JSONField(default=dict, blank=True)  # Search preferences, filters, etc.
    social_links = models.JSONField(default=dict, blank=True)  # LinkedIn, Twitter, etc.
    verification_documents = models.JSONField(default=list, blank=True)  # Document uploads
    saved_searches = models.JSONField(default=list, blank=True)  # Saved property searches
    
    # Statistics
    properties_posted = models.IntegerField(default=0)
    properties_sold = models.IntegerField(default=0)
    inquiries_received = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_userprofile'
    
    def __str__(self):
        return f"Profile of {self.user.get_full_name()}"

class FavoriteProperty(models.Model):
    """
    Track user's favorite properties
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    property_id = models.CharField(max_length=50)  # MongoDB ObjectId as string
    property_title = models.CharField(max_length=200)  # Cache for quick access
    property_price = models.DecimalField(max_digits=12, decimal_places=2)  # Cache for quick access
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'accounts_favorite_property'
        unique_together = ['user', 'property_id']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s favorite: {self.property_title}"
