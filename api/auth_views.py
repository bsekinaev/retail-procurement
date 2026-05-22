from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from users.serializers import RegisterSerializer,UserProfileSerializer
from users.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required



class LoginView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'Сообщение': 'Пользователь зарегистрирован. Проверьте Email для подтверждения'},
                        status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request):
    token = request.query_params.get('token')
    if not token:
        return Response({'Ошибка': 'Токен не указан'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(verification_token=token, is_verified=False).first()
    if not user:
        return Response({'Ошибка':'Неверный или уже использованный токен'}, status=status.HTTP_404_NOT_FOUND)
    user.is_verified = True
    user.is_active = True
    user.verification_token = None
    user.save()
    return Response({'Сообщение':'Email успешно подтвержден'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)

@login_required
def social_token_view(request):
    # Отдаёт JWT access/refresh для аутентифицированного через соцсеть пользователя
    user = request.user
    refresh = RefreshToken.for_user(user)
    return JsonResponse({
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    })