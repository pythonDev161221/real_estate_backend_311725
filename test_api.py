#!/usr/bin/env python3
"""
Test script to verify API endpoints are working with MongoDB
"""

import requests
import json
import time

def test_api_endpoints():
    """Test the MongoDB-based API endpoints"""
    
    base_url = "http://localhost:8000/api"
    
    print("Testing MongoDB-based API endpoints...")
    print("=" * 50)
    
    # Test 1: Get empty properties list
    try:
        response = requests.get(f"{base_url}/properties/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET /api/properties/ - Status: {response.status_code}")
            print(f"   Properties count: {data.get('count', 0)}")
        else:
            print(f"❌ GET /api/properties/ - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ GET /api/properties/ failed: {str(e)}")
        print("   Make sure Django server is running: pipenv run python manage.py runserver")
        return False
    
    # Test 2: Create a new property
    test_property = {
        "title": "API Test Property",
        "description": "Test property created via API",
        "property_type": "house",
        "status": "sale",
        "price": 350000,
        "bedrooms": 4,
        "bathrooms": 3,
        "area": 2000,
        "address": "456 API Test Ave",
        "city": "Test City",
        "state": "Test State",
        "zip_code": "54321",
        "latitude": 41.8781,
        "longitude": -87.6298,
        "featured": True
    }
    
    try:
        response = requests.post(
            f"{base_url}/properties/",
            json=test_property,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 201:
            created_property = response.json()
            property_id = created_property.get('id')
            print(f"✅ POST /api/properties/ - Status: {response.status_code}")
            print(f"   Created property ID: {property_id}")
        else:
            print(f"❌ POST /api/properties/ - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ POST /api/properties/ failed: {str(e)}")
        return False
    
    # Test 3: Get property by ID
    try:
        response = requests.get(f"{base_url}/properties/{property_id}/", timeout=5)
        if response.status_code == 200:
            property_data = response.json()
            print(f"✅ GET /api/properties/{property_id}/ - Status: {response.status_code}")
            print(f"   Property title: {property_data.get('title')}")
        else:
            print(f"❌ GET /api/properties/{property_id}/ - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ GET /api/properties/{property_id}/ failed: {str(e)}")
        return False
    
    # Test 4: Get statistics
    try:
        response = requests.get(f"{base_url}/stats/", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ GET /api/stats/ - Status: {response.status_code}")
            print(f"   Total properties: {stats.get('total_properties')}")
            print(f"   For sale: {stats.get('for_sale')}")
            print(f"   Featured: {stats.get('featured')}")
        else:
            print(f"❌ GET /api/stats/ - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ GET /api/stats/ failed: {str(e)}")
        return False
    
    # Test 5: Update property
    update_data = {"title": "Updated API Test Property", "price": 375000}
    try:
        response = requests.put(
            f"{base_url}/properties/{property_id}/",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 200:
            updated_property = response.json()
            print(f"✅ PUT /api/properties/{property_id}/ - Status: {response.status_code}")
            print(f"   Updated title: {updated_property.get('title')}")
            print(f"   Updated price: {updated_property.get('price')}")
        else:
            print(f"❌ PUT /api/properties/{property_id}/ - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ PUT /api/properties/{property_id}/ failed: {str(e)}")
        return False
    
    # Test 6: Delete property
    try:
        response = requests.delete(f"{base_url}/properties/{property_id}/", timeout=5)
        if response.status_code == 204:
            print(f"✅ DELETE /api/properties/{property_id}/ - Status: {response.status_code}")
        else:
            print(f"❌ DELETE /api/properties/{property_id}/ - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ DELETE /api/properties/{property_id}/ failed: {str(e)}")
        return False
    
    print("=" * 50)
    print("✅ All API tests passed! MongoDB integration is working perfectly.")
    return True

if __name__ == '__main__':
    # Wait a moment for server to start if it's just started
    print("Waiting for Django server to be ready...")
    time.sleep(2)
    
    success = test_api_endpoints()
    if not success:
        print("\n💡 To run these tests:")
        print("   1. Start Django server: pipenv run python manage.py runserver")
        print("   2. Run this test: python test_api.py")
        exit(1)