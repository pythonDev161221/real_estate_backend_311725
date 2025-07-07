from django.urls import path
from . import views

urlpatterns = [
    path('properties/', views.PropertyListAPIView.as_view(), name='api_property_list'),
    path('properties/<int:pk>/', views.PropertyDetailAPIView.as_view(), name='api_property_detail'),
    path('stats/', views.property_stats, name='api_property_stats'),
]