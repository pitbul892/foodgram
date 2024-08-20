import base64

from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from rest_framework import   serializers
from users.models import CustomUser, Subscriptions

User = get_user_model()
class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)
class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True, required=False)
    avatar = Base64ImageField(required=False, allow_null=True)
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'avatar', 'is_subscribed')
    def get_is_subscribed(self, user):
        return Subscriptions.objects.filter(user=user).exists()
 
class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    class Meta:
        model = User
        fields = ('avatar',)

class SubscribeSerializer(serializers.ModelSerializer):
    # user = UserSerializer(many=True)
    class Meta:
        model = CustomUser
        fields = 'id', 'email', 'username', 'first_name', 'last_name', 'avatar', 'is_subscribed'