from django.http import JsonResponse

def health_check(request):
    """
    A simple health check endpoint that returns a 200 OK response.
    Used by DigitalOcean's App Platform to verify the application is running.
    """
    return JsonResponse({"status": "healthy"}, status=200)