from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Property

def property_list(request):
    properties = Property.objects.all()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        properties = properties.filter(status=status)
    
    # Filter by property type
    property_type = request.GET.get('type')
    if property_type:
        properties = properties.filter(property_type=property_type)
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)
    
    # Pagination
    paginator = Paginator(properties, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'properties': page_obj.object_list,
        'property_types': Property.PROPERTY_TYPES,
        'status_choices': Property.STATUS_CHOICES,
    }
    return render(request, 'webapp/property_list.html', context)

def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    context = {
        'property': property,
    }
    return render(request, 'webapp/property_detail.html', context)

def home(request):
    featured_properties = Property.objects.filter(featured=True)[:6]
    recent_properties = Property.objects.all()[:6]
    
    context = {
        'featured_properties': featured_properties,
        'recent_properties': recent_properties,
    }
    return render(request, 'webapp/home.html', context)
