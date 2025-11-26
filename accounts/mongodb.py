"""
MongoDB connection utility for user management
"""
from pymongo import MongoClient
from django.conf import settings
from urllib.parse import quote_plus
import re

class MongoDB:
    """MongoDB connection handler"""
    
    _client = None
    _db = None
    
    @classmethod
    def _fix_mongodb_uri(cls, uri):
        """
        Fix MongoDB URI by properly encoding username and password
        This handles cases where @ symbols in passwords aren't properly encoded
        """
        try:
            print(f"Original URI: {uri}")  # Debug log
            
            # Pattern to match mongodb+srv://username:password@host...
            pattern = r'mongodb\+srv://([^:]+):([^@]+)@(.+)'
            match = re.match(pattern, uri)
            
            if match:
                username, password, rest = match.groups()
                print(f"Extracted - Username: {username}, Password: {password[:5]}***")  # Debug log (partial password)
                
                # Always encode the password to ensure it's properly escaped
                encoded_password = quote_plus(password)
                fixed_uri = f"mongodb+srv://{username}:{encoded_password}@{rest}"
                print(f"Fixed URI: {fixed_uri}")  # Debug log
                return fixed_uri
            else:
                print("URI pattern did not match, returning original")
                return uri
        except Exception as e:
            print(f"Error fixing URI: {e}")
            return uri
    
    @classmethod
    def get_client(cls):
        """Get MongoDB client instance"""
        if cls._client is None:
            try:
                # Ensure the URI is properly encoded
                original_uri = settings.MONGO_URI
                fixed_uri = cls._fix_mongodb_uri(original_uri)
                print(f"Attempting MongoDB connection...")
                cls._client = MongoClient(fixed_uri)
                print("MongoDB client created successfully")
            except Exception as e:
                print(f"MongoDB connection error: {e}")
                # Try alternative approach - manually build the URI
                try:
                    # Extract components manually
                    if 'senthamizhselvansm_db_user:Selva@123@' in original_uri:
                        print("Detected problematic password, fixing manually...")
                        fixed_manual = original_uri.replace(
                            'senthamizhselvansm_db_user:Selva@123@',
                            'senthamizhselvansm_db_user:Selva%40123@'
                        )
                        print(f"Manual fix result: {fixed_manual}")
                        cls._client = MongoClient(fixed_manual)
                        print("MongoDB client created with manual fix")
                    else:
                        raise e
                except Exception as e2:
                    print(f"Manual fix also failed: {e2}")
                    raise e
        return cls._client
    
    @classmethod
    def get_database(cls):
        """Get MongoDB database instance"""
        if cls._db is None:
            client = cls.get_client()
            cls._db = client[settings.MONGO_DB_NAME]
        return cls._db
    
    @classmethod
    def get_users_collection(cls):
        """Get users collection"""
        db = cls.get_database()
        return db['users']
    
    @classmethod
    def get_scans_collection(cls):
        """Get scans collection"""
        db = cls.get_database()
        return db['scans']
