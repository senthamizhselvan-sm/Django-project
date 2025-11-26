from django.http import JsonResponse
from accounts.mongodb import MongoDB
from django.conf import settings

def health_check(request):
    """Health check endpoint to verify MongoDB connection"""
    try:
        # Test MongoDB connection
        client = MongoDB.get_client()
        if client is None:
            return JsonResponse({
                'status': 'error',
                'message': 'MongoDB client is None',
                'mongo_uri': settings.MONGO_URI[:50] + '...' if len(settings.MONGO_URI) > 50 else settings.MONGO_URI
            }, status=500)
        
        # Test database access
        db = MongoDB.get_database()
        if db is None:
            return JsonResponse({
                'status': 'error',
                'message': 'MongoDB database access failed',
                'db_name': settings.MONGO_DB_NAME
            }, status=500)
        
        # Test collection access
        users_collection = MongoDB.get_users_collection()
        user_count = users_collection.count_documents({})
        
        return JsonResponse({
            'status': 'success',
            'message': 'All systems operational',
            'mongodb': {
                'connected': True,
                'database': settings.MONGO_DB_NAME,
                'user_count': user_count
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Health check failed: {str(e)}',
            'mongo_uri': settings.MONGO_URI[:50] + '...' if len(settings.MONGO_URI) > 50 else settings.MONGO_URI
        }, status=500)