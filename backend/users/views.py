from djoser import views
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from users.models import CustomUser
from .serializers import UserSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
User = get_user_model()

# # class UserViewSet(viewsets.ModelViewSet):
# class UserViewSet(views.UserViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [AllowAny, ]