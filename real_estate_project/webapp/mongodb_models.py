from pymongo import MongoClient
from django.conf import settings
from datetime import datetime
from bson import ObjectId
import os

class MongoDBConnection:
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
        return cls._instance
    
    def get_client(self):
        if self._client is None:
            self._client = MongoClient(settings.MONGODB_SETTINGS['host'])
        return self._client
    
    def get_database(self):
        client = self.get_client()
        return client[settings.MONGODB_SETTINGS['db']]
    
    def get_collection(self, collection_name):
        db = self.get_database()
        return db[collection_name]

class PropertyMongoDB:
    """MongoDB-based Property model"""
    
    def __init__(self, **kwargs):
        self.collection = MongoDBConnection().get_collection('properties')
        
        # Initialize fields
        self._id = kwargs.get('_id')
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', '')
        self.property_type = kwargs.get('property_type', 'house')
        self.status = kwargs.get('status', 'sale')
        self.price = kwargs.get('price', 0.0)
        self.bedrooms = kwargs.get('bedrooms', 0)
        self.bathrooms = kwargs.get('bathrooms', 0)
        self.area = kwargs.get('area', 0)
        self.address = kwargs.get('address', '')
        self.city = kwargs.get('city', '')
        self.state = kwargs.get('state', '')
        self.zip_code = kwargs.get('zip_code', '')
        self.latitude = kwargs.get('latitude', 0.0)
        self.longitude = kwargs.get('longitude', 0.0)
        self.image = kwargs.get('image', '')
        self.featured = kwargs.get('featured', False)
        self.created_at = kwargs.get('created_at', datetime.now())
        self.updated_at = kwargs.get('updated_at', datetime.now())
        
        # User ownership and permissions
        self.owner_id = kwargs.get('owner_id', None)  # User ID who owns this property
        self.created_by_id = kwargs.get('created_by_id', None)  # User ID who created this listing
        self.is_public = kwargs.get('is_public', True)  # Whether property is publicly visible
        self.contact_info = kwargs.get('contact_info', {})  # Owner contact details
    
    @property
    def id(self):
        return str(self._id) if self._id else None
    
    def save(self):
        """Save the property to MongoDB"""
        data = self.to_dict()
        
        if self._id:
            # Update existing document
            data['updated_at'] = datetime.now()
            self.collection.update_one(
                {'_id': ObjectId(self._id)},
                {'$set': data}
            )
        else:
            # Create new document
            data['created_at'] = datetime.now()
            data['updated_at'] = datetime.now()
            result = self.collection.insert_one(data)
            self._id = result.inserted_id
        
        return self
    
    def delete(self):
        """Delete the property from MongoDB"""
        if self._id:
            self.collection.delete_one({'_id': ObjectId(self._id)})
            return True
        return False
    
    def to_dict(self):
        """Convert property to dictionary"""
        data = {
            'title': self.title,
            'description': self.description,
            'property_type': self.property_type,
            'status': self.status,
            'price': self.price,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'area': self.area,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'image': self.image,
            'featured': self.featured,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'owner_id': self.owner_id,
            'created_by_id': self.created_by_id,
            'is_public': self.is_public,
            'contact_info': self.contact_info
        }
        
        if self._id:
            data['_id'] = ObjectId(self._id) if isinstance(self._id, str) else self._id
            
        return data
    
    @classmethod
    def find_all(cls, filters=None, sort=None, limit=None):
        """Find all properties with optional filters"""
        collection = MongoDBConnection().get_collection('properties')
        
        query = filters or {}
        cursor = collection.find(query)
        
        if sort:
            cursor = cursor.sort(sort)
        
        if limit:
            cursor = cursor.limit(limit)
        
        properties = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            properties.append(cls(**doc))
        
        return properties
    
    @classmethod
    def find_by_id(cls, property_id):
        """Find property by ID"""
        collection = MongoDBConnection().get_collection('properties')
        
        try:
            doc = collection.find_one({'_id': ObjectId(property_id)})
            if doc:
                doc['_id'] = str(doc['_id'])
                return cls(**doc)
        except:
            pass
        
        return None
    
    @classmethod
    def count(cls, filters=None):
        """Count properties with optional filters"""
        collection = MongoDBConnection().get_collection('properties')
        return collection.count_documents(filters or {})
    
    @classmethod
    def search(cls, search_term):
        """Search properties by title, description, city, or state"""
        if not search_term:
            return cls.find_all()
        
        filters = {
            '$or': [
                {'title': {'$regex': search_term, '$options': 'i'}},
                {'description': {'$regex': search_term, '$options': 'i'}},
                {'city': {'$regex': search_term, '$options': 'i'}},
                {'state': {'$regex': search_term, '$options': 'i'}}
            ]
        }
        
        return cls.find_all(filters)
    
    def __str__(self):
        return self.title