from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Property
from .mongodb_models import PropertyMongoDB

def property_list(request):
    # Build filters for MongoDB
    filters = {}
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        filters['status'] = status
    
    # Filter by property type
    property_type = request.GET.get('type')
    if property_type:
        filters['property_type'] = property_type
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price or max_price:
        price_filter = {}
        if min_price:
            price_filter['$gte'] = float(min_price)
        if max_price:
            price_filter['$lte'] = float(max_price)
        filters['price'] = price_filter
    
    # Get properties from MongoDB
    properties = PropertyMongoDB.find_all(
        filters=filters,
        sort=[('created_at', -1)]
    )
    
    # Simple pagination (you might want to improve this)
    from django.core.paginator import Paginator
    paginator = Paginator(properties, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Property types and status choices for filters
    property_types = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('condo', 'Condo'),
        ('townhouse', 'Townhouse'),
        ('land', 'Land'),
    ]
    
    status_choices = [
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
    ]
    
    context = {
        'page_obj': page_obj,
        'properties': page_obj.object_list,
        'property_types': property_types,
        'status_choices': status_choices,
    }
    return render(request, 'webapp/property_list.html', context)

def property_detail(request, pk):
    property = PropertyMongoDB.find_by_id(pk)
    if not property:
        from django.http import Http404
        raise Http404("Property not found")
    
    context = {
        'property': property,
    }
    return render(request, 'webapp/property_detail.html', context)

def home(request):
    featured_properties = PropertyMongoDB.find_all(
        filters={'featured': True},
        sort=[('created_at', -1)],
        limit=6
    )
    recent_properties = PropertyMongoDB.find_all(
        sort=[('created_at', -1)],
        limit=6
    )
    
    context = {
        'featured_properties': featured_properties,
        'recent_properties': recent_properties,
    }
    return render(request, 'webapp/home.html', context)
