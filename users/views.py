from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

def social_complete(request):
    user = request.user
    if user.is_authenticated:
        refresh = RefreshToken.for_user(user)
        return redirect(f'{settings.FRONTEND_URL}/login.html?token={refresh.access_token}')
    return redirect('/login.html')