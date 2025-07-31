#!/usr/bin/env python3
"""
Add sample data to MongoDB for testing
"""

import os
import sys
import django
from datetime import datetime

# Add the project directory to Python path
sys.path.append('/home/ormon/Documents/projects/real_estate_cloude_070725/real_estate_django/real_estate_project')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_project.settings')
django.setup()

from webapp.mongodb_models import PropertyMongoDB

def add_sample_properties():
    """Add sample properties to MongoDB"""
    
    sample_properties = [
        {
            'title': 'Modern Family Home',
            'description': 'Beautiful 4-bedroom family home with spacious living areas, modern kitchen, and large backyard. Perfect for families looking for comfort and style.',
            'property_type': 'house',
            'status': 'sale',
            'price': 450000,
            'bedrooms': 4,
            'bathrooms': 3,
            'area': 2200,
            'address': '123 Maple Street',
            'city': 'Springfield',
            'state': 'Illinois',
            'zip_code': '62701',
            'latitude': 39.7817,
            'longitude': -89.6501,
            'featured': True
        },
        {
            'title': 'Downtown Luxury Apartment',
            'description': 'Stunning 2-bedroom apartment in the heart of downtown. Features floor-to-ceiling windows, modern amenities, and city views.',
            'property_type': 'apartment',
            'status': 'rent',
            'price': 2500,
            'bedrooms': 2,
            'bathrooms': 2,
            'area': 1200,
            'address': '456 Main Avenue',
            'city': 'Chicago',
            'state': 'Illinois',
            'zip_code': '60601',
            'latitude': 41.8781,
            'longitude': -87.6298,
            'featured': True
        },
        {
            'title': 'Cozy Suburban Condo',
            'description': 'Well-maintained 3-bedroom condo in quiet suburban neighborhood. Includes garage, patio, and access to community pool.',
            'property_type': 'condo',
            'status': 'sale',
            'price': 280000,
            'bedrooms': 3,
            'bathrooms': 2,
            'area': 1400,
            'address': '789 Oak Drive',
            'city': 'Naperville',
            'state': 'Illinois',
            'zip_code': '60540',
            'latitude': 41.7508,
            'longitude': -88.1535,
            'featured': False
        },
        {
            'title': 'Historic Townhouse',
            'description': 'Charming 3-story townhouse with original hardwood floors, exposed brick walls, and modern updates throughout.',
            'property_type': 'townhouse',
            'status': 'sale',
            'price': 375000,
            'bedrooms': 3,
            'bathrooms': 2,
            'area': 1800,
            'address': '321 Heritage Lane',
            'city': 'Evanston',
            'state': 'Illinois',
            'zip_code': '60201',
            'latitude': 42.0451,
            'longitude': -87.6877,
            'featured': False
        },
        {
            'title': 'Spacious Rental Home',
            'description': 'Large 5-bedroom house perfect for families or roommates. Features open floor plan, updated kitchen, and fenced yard.',
            'property_type': 'house',
            'status': 'rent',
            'price': 3200,
            'bedrooms': 5,
            'bathrooms': 3,
            'area': 2800,
            'address': '654 Pine Street',
            'city': 'Aurora',
            'state': 'Illinois',
            'zip_code': '60505',
            'latitude': 41.7606,
            'longitude': -88.3201,
            'featured': False
        },
        {
            'title': 'Investment Land Opportunity',
            'description': 'Prime development land in growing area. Zoned for residential development with utilities available.',
            'property_type': 'land',
            'status': 'sale',
            'price': 150000,
            'bedrooms': 0,
            'bathrooms': 0,
            'area': 43560,  # 1 acre
            'address': '999 Development Road',
            'city': 'Plainfield',
            'state': 'Illinois',
            'zip_code': '60586',
            'latitude': 41.6270,
            'longitude': -88.2120,
            'featured': False
        },
        {
            'title': 'Luxury Penthouse',
            'description': 'Exclusive penthouse with panoramic city views, premium finishes, and private terrace. The epitome of urban luxury living.',
            'property_type': 'apartment',
            'status': 'sale',
            'price': 850000,
            'bedrooms': 3,
            'bathrooms': 3,
            'area': 2000,
            'address': '100 Skyline Tower',
            'city': 'Chicago',
            'state': 'Illinois',
            'zip_code': '60611',
            'latitude': 41.8902,
            'longitude': -87.6226,
            'featured': True
        },
        {
            'title': 'Student Housing Near Campus',
            'description': 'Perfect for students! 4-bedroom house walking distance to university. Recently renovated with modern amenities.',
            'property_type': 'house',
            'status': 'rent',
            'price': 2000,
            'bedrooms': 4,
            'bathrooms': 2,
            'area': 1600,
            'address': '888 College Avenue',
            'city': 'Champaign',
            'state': 'Illinois',
            'zip_code': '61820',
            'latitude': 40.1106,
            'longitude': -88.2073,
            'featured': False
        }
    ]
    
    print("Adding sample properties to MongoDB...")
    
    # Clear existing data
    PropertyMongoDB.find_all()  # Initialize connection
    from webapp.mongodb_models import MongoDBConnection
    collection = MongoDBConnection().get_collection('properties')
    collection.delete_many({})
    print("Cleared existing properties")
    
    # Add sample properties
    added_count = 0
    for prop_data in sample_properties:
        try:
            property_obj = PropertyMongoDB(**prop_data)
            property_obj.save()
            added_count += 1
            print(f"✅ Added: {property_obj.title}")
        except Exception as e:
            print(f"❌ Failed to add {prop_data['title']}: {str(e)}")
    
    print(f"\n🎉 Successfully added {added_count} sample properties!")
    
    # Verify the data
    all_properties = PropertyMongoDB.find_all()
    print(f"📊 Total properties in database: {len(all_properties)}")
    
    # Show stats
    for_sale = PropertyMongoDB.count({'status': 'sale'})
    for_rent = PropertyMongoDB.count({'status': 'rent'})
    featured = PropertyMongoDB.count({'featured': True})
    
    print(f"   - For Sale: {for_sale}")
    print(f"   - For Rent: {for_rent}")
    print(f"   - Featured: {featured}")

if __name__ == '__main__':
    try:
        add_sample_properties()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)