#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite to MongoDB
Run this script from the Django project directory after setting up MongoDB configuration
"""

import os
import sys
import django
import sqlite3
from pymongo import MongoClient
from datetime import datetime
import json

# Add the project directory to Python path
sys.path.append('/home/ormon/Documents/projects/real_estate_cloude_070725/real_estate_django/real_estate_project')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_project.settings')
django.setup()

def migrate_sqlite_to_mongodb():
    # Connect to SQLite database
    sqlite_db_path = '/home/ormon/Documents/projects/real_estate_cloude_070725/real_estate_django/real_estate_project/db.sqlite3'
    
    if not os.path.exists(sqlite_db_path):
        print("SQLite database not found. No data to migrate.")
        return
    
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to MongoDB
    mongo_client = MongoClient('mongodb://localhost:27017/')
    mongo_db = mongo_client['real_estate_db']
    properties_collection = mongo_db['webapp_property']
    
    # Clear existing data in MongoDB collection
    properties_collection.delete_many({})
    print("Cleared existing MongoDB collection")
    
    # Get data from SQLite
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='webapp_property';")
    if not sqlite_cursor.fetchone():
        print("No webapp_property table found in SQLite database")
        return
    
    sqlite_cursor.execute("""
        SELECT id, title, description, property_type, status, price, 
               bedrooms, bathrooms, area, address, city, state, zip_code, 
               latitude, longitude, image, featured, created_at, updated_at
        FROM webapp_property
    """)
    
    properties = sqlite_cursor.fetchall()
    
    if not properties:
        print("No properties found in SQLite database")
        return
    
    # Convert and insert into MongoDB
    mongodb_documents = []
    for prop in properties:
        doc = {
            'id': prop[0],
            'title': prop[1],
            'description': prop[2],
            'property_type': prop[3],
            'status': prop[4],
            'price': float(prop[5]) if prop[5] else 0.0,
            'bedrooms': prop[6],
            'bathrooms': prop[7],
            'area': prop[8],
            'address': prop[9],
            'city': prop[10],
            'state': prop[11],
            'zip_code': prop[12],
            'latitude': float(prop[13]) if prop[13] else 0.0,
            'longitude': float(prop[14]) if prop[14] else 0.0,
            'image': prop[15] if prop[15] else '',
            'featured': bool(prop[16]),
            'created_at': prop[17],
            'updated_at': prop[18]
        }
        mongodb_documents.append(doc)
    
    # Insert into MongoDB
    if mongodb_documents:
        result = properties_collection.insert_many(mongodb_documents)
        print(f"Successfully migrated {len(result.inserted_ids)} properties to MongoDB")
    
    # Close connections
    sqlite_conn.close()
    mongo_client.close()
    
    print("Migration completed successfully!")

if __name__ == '__main__':
    try:
        migrate_sqlite_to_mongodb()
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        sys.exit(1)