"""
MongoDB connection utility for user management
"""
from pymongo import MongoClient
from django.conf import settings

class MongoDB:
    """MongoDB connection handler"""
    
    _client = None
    _db = None
    
    @classmethod
    def get_client(cls):
        """Get MongoDB client instance"""
        if cls._client is None:
            cls._client = MongoClient(settings.MONGO_URI)
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
