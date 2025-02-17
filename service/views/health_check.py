from django.http import JsonResponse
from django.db import connection
from django.db.utils import OperationalError

def health_check(request):
    """
    Health check endpoint that verifies database connectivity.
    Used by DigitalOcean's App Platform to verify the application is running.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return JsonResponse({"status": "healthy", "database": "connected"}, status=200)
    except OperationalError:
        return JsonResponse(
            {"status": "unhealthy", "database": "disconnected"}, 
            status=503
        )
