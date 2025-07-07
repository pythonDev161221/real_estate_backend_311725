from rest_framework import serializers
from webapp.models import Property

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'property_type', 'status', 
            'price', 'bedrooms', 'bathrooms', 'area', 'address', 
            'city', 'state', 'zip_code', 'image', 'featured', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class PropertyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'property_type', 'status', 'price', 
            'bedrooms', 'bathrooms', 'area', 'city', 'state', 
            'image', 'featured', 'created_at'
        ]