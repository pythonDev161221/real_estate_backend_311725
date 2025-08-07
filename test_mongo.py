#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/home/ormon/Documents/projects/real_estate_cloude_070725/real_estate_django/real_estate_project')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_project.settings')
django.setup()

from webapp.mongodb_models import PropertyMongoDB

try:
    count = PropertyMongoDB.count()
    print(f'MongoDB Properties count: {count}')
    if count > 0:
        properties = PropertyMongoDB.find_all(limit=3)
        print('First 3 properties:')
        for i, prop in enumerate(properties):
            print(f'{i+1}. {prop.title} - ${prop.price} in {prop.city}')
    else:
        print('No properties found in MongoDB')
except Exception as e:
    print(f'MongoDB connection error: {e}')