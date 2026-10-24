from django.contrib.auth import login
from django.contrib.auth.models import User


class AutoLoginMiddleware:
    """
    Ensures any visitor is automatically authenticated with a primary profile
    (e.g. Rithi or first available active account) so they can explore, post,
    like, bookmark, and comment immediately without encountering any login page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            # Pick the primary user (Rithi or fallback to alex_rivera or first user)
            user = (
                User.objects.filter(email='rithi@gmail.com').first()
                or User.objects.filter(username='rithi@gmail.com').first()
                or User.objects.filter(username='alex_rivera').first()
                or User.objects.exclude(is_superuser=True).first()
                or User.objects.first()
            )
            if user:
                login(request, user)
                request.user = user

        response = self.get_response(request)
        return response
