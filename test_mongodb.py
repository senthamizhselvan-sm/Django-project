"""
Test MongoDB connection and debug URI issues
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'radiology.settings')
django.setup()

from accounts.mongodb import MongoDB
from django.conf import settings

def test_mongodb_connection():
    print("=== MongoDB Connection Test ===")
    print(f"MongoDB URI from settings: {settings.MONGO_URI}")
    print(f"MongoDB DB Name: {settings.MONGO_DB_NAME}")
    
    try:
        # Test connection
        client = MongoDB.get_client()
        db = MongoDB.get_database()
        
        # Test database operation
        collections = db.list_collection_names()
        print(f"✅ Connection successful!")
        print(f"Available collections: {collections}")
        
        # Test users collection access
        users_collection = MongoDB.get_users_collection()
        user_count = users_collection.count_documents({})
        print(f"Users collection accessible: {user_count} users found")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mongodb_connection()