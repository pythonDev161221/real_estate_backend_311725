from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, FavoriteProperty

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for custom User model
    """
    list_display = ('email', 'username', 'first_name', 'last_name', 'user_type', 'is_verified', 'is_active', 'created_at')
    list_filter = ('user_type', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'company_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'avatar', 'bio', 'location')}),
        ('Real Estate Info', {'fields': ('user_type', 'company_name', 'license_number', 'website')}),
        ('Verification', {'fields': ('is_verified', 'is_phone_verified', 'is_email_verified')}),
        ('Preferences', {'fields': ('preferred_contact', 'show_contact_info', 'receive_marketing')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'user_type', 'password1', 'password2'),
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserProfile model
    """
    list_display = ('user', 'properties_posted', 'properties_sold', 'inquiries_received', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Statistics', {'fields': ('properties_posted', 'properties_sold', 'inquiries_received')}),
        ('Extended Data', {'fields': ('preferences', 'social_links', 'saved_searches')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(FavoriteProperty)
class FavoritePropertyAdmin(admin.ModelAdmin):
    """
    Admin configuration for FavoriteProperty model
    """
    list_display = ('user', 'property_title', 'property_price', 'property_id', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'property_title', 'property_id')
    readonly_fields = ('added_at',)
    
    fieldsets = (
        ('User & Property', {'fields': ('user', 'property_id', 'property_title', 'property_price')}),
        ('Timestamp', {'fields': ('added_at',)}),
    )
