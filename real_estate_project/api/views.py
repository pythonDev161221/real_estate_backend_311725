from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from webapp.models import Property
from .serializers import PropertySerializer, PropertyListSerializer

class PropertyListAPIView(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertyListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'status', 'featured']
    search_fields = ['title', 'description', 'city', 'state']
    ordering_fields = ['price', 'created_at', 'area']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Property.objects.all()
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        return queryset

class PropertyDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

@api_view(['GET'])
def property_stats(request):
    total_properties = Property.objects.count()
    for_sale = Property.objects.filter(status='sale').count()
    for_rent = Property.objects.filter(status='rent').count()
    featured = Property.objects.filter(featured=True).count()
    
    return Response({
        'total_properties': total_properties,
        'for_sale': for_sale,
        'for_rent': for_rent,
        'featured': featured
    })
