from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from webapp.mongodb_models import PropertyMongoDB
from accounts.models import User
from accounts.serializers import PublicUserSerializer
from datetime import datetime
from bson import ObjectId

def property_to_dict(prop, include_owner_info=False, request_user=None):
    """Convert PropertyMongoDB instance to dictionary for serialization"""
    data = {
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
        'updated_at': prop.updated_at.isoformat() if prop.updated_at else None,
        'is_public': prop.is_public
    }
    
    # Add owner information if requested or if user is the owner
    if include_owner_info or (request_user and request_user.is_authenticated and 
                             (str(request_user.id) == str(prop.owner_id) or request_user.is_staff)):
        data['owner_id'] = prop.owner_id
        data['created_by_id'] = prop.created_by_id
        
        # Add owner contact info if available and user has permission
        if prop.contact_info:
            data['contact_info'] = prop.contact_info
        
        # Try to get owner details
        if prop.owner_id:
            try:
                owner = User.objects.get(id=prop.owner_id)
                data['owner'] = PublicUserSerializer(owner).data
            except User.DoesNotExist:
                data['owner'] = None
    
    return data

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
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
        
        # Convert to dictionaries with appropriate permissions
        properties_data = [property_to_dict(prop, include_owner_info=True, request_user=request.user) for prop in properties]
        
        # Simple pagination response format to match DRF pagination
        total_count = len(properties_data)
        
        return Response({
            'count': total_count,
            'next': None,  # Simple implementation - no pagination for now
            'previous': None,
            'results': properties_data
        })
    
    elif request.method == 'POST':
        # Create new property - requires authentication
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required to create properties'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user can post properties
        if not request.user.can_post_properties:
            return Response({
                'error': 'Only verified sellers and agents can post properties. Please verify your account.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            data = request.data
            
            # Set owner and creator information
            contact_info = {}
            if request.user.show_contact_info:
                if request.user.email:
                    contact_info['email'] = request.user.email
                if request.user.phone:
                    contact_info['phone'] = request.user.phone
                contact_info['preferred_contact'] = request.user.preferred_contact
            
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
                featured=bool(data.get('featured', False)),
                owner_id=str(request.user.id),
                created_by_id=str(request.user.id),
                is_public=bool(data.get('is_public', True)),
                contact_info=contact_info
            )
            
            property_obj.save()
            
            # Update user's property count
            if hasattr(request.user, 'profile_extended'):
                profile = request.user.profile_extended
                profile.properties_posted += 1
                profile.save()
            
            return Response(
                property_to_dict(property_obj, include_owner_info=True, request_user=request.user), 
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def property_detail_mongodb(request, pk):
    """MongoDB-based property detail endpoint"""
    
    try:
        property_obj = PropertyMongoDB.find_by_id(pk)
        if not property_obj:
            return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)
    except:
        return Response({'error': 'Invalid property ID'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'GET':
        return Response(property_to_dict(property_obj, include_owner_info=True, request_user=request.user))
    
    elif request.method == 'PUT':
        # Check ownership for updates
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user owns the property or is staff
        if (str(request.user.id) != str(property_obj.owner_id) and 
            str(request.user.id) != str(property_obj.created_by_id) and 
            not request.user.is_staff):
            return Response({'error': 'You can only edit your own properties'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
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
            property_obj.is_public = bool(data.get('is_public', property_obj.is_public))
            
            property_obj.save()
            return Response(property_to_dict(property_obj, include_owner_info=True, request_user=request.user))
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Check ownership for deletion
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user owns the property or is staff
        if (str(request.user.id) != str(property_obj.owner_id) and 
            str(request.user.id) != str(property_obj.created_by_id) and 
            not request.user.is_staff):
            return Response({'error': 'You can only delete your own properties'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        property_obj.delete()
        
        # Update user's property count
        if hasattr(request.user, 'profile_extended'):
            profile = request.user.profile_extended
            if profile.properties_posted > 0:
                profile.properties_posted -= 1
                profile.save()
        
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