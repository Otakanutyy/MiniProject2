from django.utils.timezone import now
from .models import APIRequestLog


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("Middleware is processing a request")  # Debugging statement

        if request.user.is_authenticated:
            print(f"Authenticated user: {request.user.username}")  # Debugging
            APIRequestLog.objects.create(
                user=request.user,
                timestamp=now(),
                ip_address=request.META.get('REMOTE_ADDR', '0.0.0.0'),
                endpoint=request.path
            )
        else:
            print("User not authenticated")  # Debugging

        response = self.get_response(request)
        return response

