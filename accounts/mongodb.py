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
    def _build_mongodb_uri(cls, original_uri):
        """
        Build a properly encoded MongoDB URI from various input formats
        Handles multiple scenarios including already encoded URIs
        """
        try:
            print(f"[MongoDB] Processing URI: {original_uri[:50]}...")
            
            # If URI is already properly formatted (has %40), use it directly
            if 'Selva%40123' in original_uri:
                print("[MongoDB] URI already properly encoded")
                return original_uri
            
            # If URI has unescaped @ in password, fix it
            if 'Selva@123' in original_uri:
                print("[MongoDB] Found unescaped password, fixing...")
                fixed_uri = original_uri.replace('Selva@123', 'Selva%40123')
                print(f"[MongoDB] Fixed URI: {fixed_uri[:50]}...")
                return fixed_uri
            
            # Try regex approach for other cases
            pattern = r'mongodb\+srv://([^:]+):([^@]+)@(.+)'
            match = re.match(pattern, original_uri)
            
            if match:
                username, password, rest = match.groups()
                print(f"[MongoDB] Extracted components - User: {username}")
                
                # Always encode password to be safe
                encoded_password = quote_plus(password)
                constructed_uri = f"mongodb+srv://{username}:{encoded_password}@{rest}"
                print(f"[MongoDB] Constructed URI: {constructed_uri[:50]}...")
                return constructed_uri
            
            print("[MongoDB] No pattern matched, using original URI")
            return original_uri
            
        except Exception as e:
            print(f"[MongoDB] Error processing URI: {e}")
            return original_uri
    
    @classmethod
    def get_client(cls):
        """Get MongoDB client instance with robust connection handling"""
        if cls._client is None:
            try:
                original_uri = settings.MONGO_URI
                print(f"[MongoDB] Original URI from settings: {original_uri[:50]}...")
                
                # Try the processed URI
                processed_uri = cls._build_mongodb_uri(original_uri)
                print(f"[MongoDB] Attempting connection with processed URI...")
                
                cls._client = MongoClient(
                    processed_uri,
                    serverSelectionTimeoutMS=5000,  # 5 second timeout
                    connectTimeoutMS=5000,
                    socketTimeoutMS=5000
                )
                
                # Test the connection
                cls._client.admin.command('ping')
                print("[MongoDB] ✅ Connection successful!")
                
            except Exception as e:
                print(f"[MongoDB] ❌ Primary connection failed: {e}")
                
                # Fallback: Try manual construction
                try:
                    print("[MongoDB] Trying manual URI construction...")
                    fallback_uri = "mongodb+srv://senthamizhselvansm_db_user:Selva%40123@cluster0.uufkp3i.mongodb.net/?appName=Cluster0"
                    
                    cls._client = MongoClient(
                        fallback_uri,
                        serverSelectionTimeoutMS=5000,
                        connectTimeoutMS=5000,
                        socketTimeoutMS=5000
                    )
                    
                    # Test the fallback connection
                    cls._client.admin.command('ping')
                    print("[MongoDB] ✅ Fallback connection successful!")
                    
                except Exception as e2:
                    print(f"[MongoDB] ❌ Fallback connection also failed: {e2}")
                    # Don't raise the error - let views handle it gracefully
                    cls._client = None
                    
        return cls._client
    
    @classmethod
    def get_database(cls):
        """Get MongoDB database instance"""
        if cls._db is None:
            client = cls.get_client()
            if client is not None:
                cls._db = client[settings.MONGO_DB_NAME]
                print(f"[MongoDB] ✅ Database '{settings.MONGO_DB_NAME}' accessed successfully")
            else:
                print("[MongoDB] ❌ Cannot access database - no client connection")
                return None
        return cls._db
    
    @classmethod
    def get_users_collection(cls):
        """Get users collection"""
        db = cls.get_database()
        if db is not None:
            return db['users']
        else:
            raise Exception("MongoDB database connection not available")
    
    @classmethod
    def get_scans_collection(cls):
        """Get scans collection"""
        db = cls.get_database()
        if db is not None:
            return db['scans']
        else:
            raise Exception("MongoDB database connection not available")
