from django.conf import settings
from django.http import HttpResponse


class SimpleCORSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get('Origin')
        allowed_origins = set(getattr(settings, 'CORS_ALLOWED_ORIGINS', []))
        if request.method == 'OPTIONS' and origin and origin in allowed_origins:
            response = HttpResponse(status=200)
        else:
            response = self.get_response(request)
        if origin and origin in allowed_origins:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        return response
