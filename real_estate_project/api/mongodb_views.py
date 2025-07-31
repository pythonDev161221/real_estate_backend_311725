from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from webapp.mongodb_models import PropertyMongoDB
from datetime import datetime
from bson import ObjectId

def property_to_dict(prop):
    """Convert PropertyMongoDB instance to dictionary for serialization"""
    return {
        'id': prop.id,
        '_id': prop.id,
        'title': prop.title,
        'description': prop.description,
        'property_type': prop.property_type,
        'status': prop.status,
        'price': prop.price,
        'bedrooms': prop.bedrooms,
        'bathrooms': prop.bathrooms,
        'area': prop.area,
        'address': prop.address,
        'city': prop.city,
        'state': prop.state,
        'zip_code': prop.zip_code,
        'latitude': prop.latitude,
        'longitude': prop.longitude,
        'image': prop.image,
        'featured': prop.featured,
        'created_at': prop.created_at.isoformat() if prop.created_at else None,
        'updated_at': prop.updated_at.isoformat() if prop.updated_at else None
    }

@api_view(['GET', 'POST'])
def property_list_mongodb(request):
    """MongoDB-based property list endpoint"""
    
    if request.method == 'GET':
        # Build filters from query parameters
        filters = {}
        
        # Filter by property type
        property_type = request.GET.get('property_type')
        if property_type:
            filters['property_type'] = property_type
        
        # Filter by status
        property_status = request.GET.get('status')
        if property_status:
            filters['status'] = property_status
        
        # Filter by featured
        featured = request.GET.get('featured')
        if featured and featured.lower() == 'true':
            filters['featured'] = True
        
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
        
        # Search functionality
        search = request.GET.get('search')
        if search:
            properties = PropertyMongoDB.search(search)
        else:
            # Sorting
            sort_by = request.GET.get('ordering', '-created_at')
            sort_field = sort_by.lstrip('-')
            sort_direction = -1 if sort_by.startswith('-') else 1
            
            # Convert Django field names to MongoDB field names
            if sort_field == 'created_at':
                sort_field = 'created_at'
            elif sort_field == 'price':
                sort_field = 'price'
            elif sort_field == 'area':
                sort_field = 'area'
            
            properties = PropertyMongoDB.find_all(
                filters=filters,
                sort=[(sort_field, sort_direction)]
            )
        
        # Convert to dictionaries
        properties_data = [property_to_dict(prop) for prop in properties]
        
        # Simple pagination response format to match DRF pagination
        total_count = len(properties_data)
        
        return Response({
            'count': total_count,
            'next': None,  # Simple implementation - no pagination for now
            'previous': None,
            'results': properties_data
        })
    
    elif request.method == 'POST':
        # Create new property
        try:
            data = request.data
            property_obj = PropertyMongoDB(
                title=data.get('title', ''),
                description=data.get('description', ''),
                property_type=data.get('property_type', 'house'),
                status=data.get('status', 'sale'),
                price=float(data.get('price', 0)),
                bedrooms=int(data.get('bedrooms', 0)),
                bathrooms=int(data.get('bathrooms', 0)),
                area=int(data.get('area', 0)),
                address=data.get('address', ''),
                city=data.get('city', ''),
                state=data.get('state', ''),
                zip_code=data.get('zip_code', ''),
                latitude=float(data.get('latitude', 0)),
                longitude=float(data.get('longitude', 0)),
                image=data.get('image', ''),
                featured=bool(data.get('featured', False))
            )
            
            property_obj.save()
            return Response(property_to_dict(property_obj), status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def property_detail_mongodb(request, pk):
    """MongoDB-based property detail endpoint"""
    
    try:
        property_obj = PropertyMongoDB.find_by_id(pk)
        if not property_obj:
            return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)
    except:
        return Response({'error': 'Invalid property ID'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'GET':
        return Response(property_to_dict(property_obj))
    
    elif request.method == 'PUT':
        try:
            data = request.data
            
            # Update fields
            property_obj.title = data.get('title', property_obj.title)
            property_obj.description = data.get('description', property_obj.description)
            property_obj.property_type = data.get('property_type', property_obj.property_type)
            property_obj.status = data.get('status', property_obj.status)
            property_obj.price = float(data.get('price', property_obj.price))
            property_obj.bedrooms = int(data.get('bedrooms', property_obj.bedrooms))
            property_obj.bathrooms = int(data.get('bathrooms', property_obj.bathrooms))
            property_obj.area = int(data.get('area', property_obj.area))
            property_obj.address = data.get('address', property_obj.address)
            property_obj.city = data.get('city', property_obj.city)
            property_obj.state = data.get('state', property_obj.state)
            property_obj.zip_code = data.get('zip_code', property_obj.zip_code)
            property_obj.latitude = float(data.get('latitude', property_obj.latitude))
            property_obj.longitude = float(data.get('longitude', property_obj.longitude))
            property_obj.image = data.get('image', property_obj.image)
            property_obj.featured = bool(data.get('featured', property_obj.featured))
            
            property_obj.save()
            return Response(property_to_dict(property_obj))
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        property_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def property_stats_mongodb(request):
    """MongoDB-based property statistics endpoint"""
    
    total_properties = PropertyMongoDB.count()
    for_sale = PropertyMongoDB.count({'status': 'sale'})
    for_rent = PropertyMongoDB.count({'status': 'rent'})
    featured = PropertyMongoDB.count({'featured': True})
    
    return Response({
        'total_properties': total_properties,
        'for_sale': for_sale,
        'for_rent': for_rent,
        'featured': featured
    })