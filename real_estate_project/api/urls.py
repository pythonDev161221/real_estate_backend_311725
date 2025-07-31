from django.urls import path
from . import views, mongodb_views

urlpatterns = [
    # MongoDB-based endpoints (primary)
    path('properties/', mongodb_views.property_list_mongodb, name='api_property_list_mongodb'),
    path('properties/<str:pk>/', mongodb_views.property_detail_mongodb, name='api_property_detail_mongodb'),
    path('stats/', mongodb_views.property_stats_mongodb, name='api_property_stats_mongodb'),
    
    # Original Django ORM endpoints (backup)
    path('django/properties/', views.PropertyListAPIView.as_view(), name='api_property_list'),
    path('django/properties/<int:pk>/', views.PropertyDetailAPIView.as_view(), name='api_property_detail'),
    path('django/stats/', views.property_stats, name='api_property_stats'),
]