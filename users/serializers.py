from rest_framework import serializers
from .models import User
import uuid
import logging
from api.tasks import send_verification_email

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'user_type')

    def create(self, validated_data):
        # Если username не передан, используем email
        username = validated_data.get('username') or validated_data['email']
        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data.get('user_type', User.UserType.CLIENT),
            is_active=False,
            is_verified=False,
            verification_token=uuid.uuid4().hex
        )

        # Асинхронная отправка письма с подтверждением
        try:
            send_verification_email.delay(user.id)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Не удалось отправить задачу Celery: {e}")
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'user_type', 'avatar_url')

    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None