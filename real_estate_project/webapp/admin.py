from django.contrib import admin
from .models import Property

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'property_type', 'status', 'price', 'city', 'state', 'featured', 'created_at']
    list_filter = ['property_type', 'status', 'featured', 'city', 'state']
    search_fields = ['title', 'description', 'address', 'city']
    list_editable = ['featured', 'status']
    readonly_fields = ['created_at', 'updated_at']
