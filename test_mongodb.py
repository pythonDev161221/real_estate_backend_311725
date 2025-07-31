#!/usr/bin/env python3
"""
Test script to verify MongoDB connection and Django integration
"""

import os
import sys
import django
from pymongo import MongoClient

# Add the project directory to Python path
sys.path.append('/home/ormon/Documents/projects/real_estate_cloude_070725/real_estate_django/real_estate_project')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_project.settings')
django.setup()

def test_mongodb_connection():
    """Test direct MongoDB connection"""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['real_estate_db']
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful")
        
        # List collections
        collections = db.list_collection_names()
        print(f"✅ Available collections: {collections}")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        return False

def test_mongodb_model():
    """Test MongoDB model operations"""
    try:
        from webapp.mongodb_models import PropertyMongoDB
        
        # Test model import
        print("✅ PropertyMongoDB model imported successfully")
        
        # Test creating a test property
        test_property = PropertyMongoDB(
            title="Test Property",
            description="Test Description",
            property_type="house",
            status="sale",
            price=250000.0,
            bedrooms=3,
            bathrooms=2,
            area=1500,
            address="123 Test St",
            city="Test City",
            state="Test State",
            zip_code="12345",
            latitude=40.7128,
            longitude=-74.0060,
            featured=False
        )
        
        # Try to save
        test_property.save()
        print("✅ Test property created successfully")
        print(f"✅ Property ID: {test_property.id}")
        
        # Try to query
        properties = PropertyMongoDB.find_all()
        print(f"✅ Property count: {len(properties)}")
        
        # Test find by ID
        found_property = PropertyMongoDB.find_by_id(test_property.id)
        if found_property:
            print("✅ Property found by ID successfully")
        
        # Test search
        search_results = PropertyMongoDB.search("Test")
        print(f"✅ Search results: {len(search_results)}")
        
        # Clean up test data
        test_property.delete()
        print("✅ Test property deleted successfully")
        
        return True
    except Exception as e:
        print(f"❌ MongoDB model test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_django_sqlite():
    """Test Django SQLite model (for admin/auth)"""
    try:
        from webapp.models import Property
        
        # Test model import
        print("✅ Django Property model imported successfully")
        
        # Don't create/test SQLite data, just verify model works
        print("✅ Django model available for admin/auth purposes")
        
        return True
    except Exception as e:
        print(f"❌ Django model test failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("Testing MongoDB Integration...")
    print("=" * 50)
    
    mongodb_ok = test_mongodb_connection()
    mongodb_model_ok = test_mongodb_model()
    django_ok = test_django_sqlite()
    
    print("=" * 50)
    if mongodb_ok and mongodb_model_ok and django_ok:
        print("✅ All tests passed! MongoDB integration is working.")
        print("\n📝 Next steps:")
        print("   1. Run: pipenv run python manage.py runserver")
        print("   2. Test API endpoints:")
        print("      - GET  http://localhost:8000/api/properties/")
        print("      - POST http://localhost:8000/api/properties/")
        print("      - GET  http://localhost:8000/api/stats/")
    else:
        print("❌ Some tests failed. Check the error messages above.")
        sys.exit(1)