from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from users.serializers import RegisterSerializer
from users.models import User

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