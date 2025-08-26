# newtask/middleware.py
from django.http import JsonResponse
from datetime import datetime

class WorkingHoursMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_hour = 9
        end_hour = 20
        current_hour = datetime.now().hour

        # Normalize path checks
        path = request.path.rstrip("/")  # removes trailing slash if present

        if path.endswith("login") or path.endswith("logout"):
            print("Middleware triggered for:", path)  # Debug log
            if current_hour < start_hour or current_hour >= end_hour:
                print("Blocked: Outside working hours")
                return JsonResponse(
                    {'error': 'Access not allowed outside working hours (9 AM - 3 PM).'},
                    status=403
                )
            print("Allowed: Inside working hours")

        return self.get_response(request)
    
    
    
    
    