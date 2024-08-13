
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from djoser import views
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from users.models import CustomUser
from .serializers import UserSerializer, AvatarSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
User = get_user_model()



class AvatarAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request):
        serializer = AvatarSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            if 'avatar' in request.data:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    
    def delete(self, request):
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# # class UserViewSet(viewsets.ModelViewSet):
# class UserViewSet(views.UserViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [AllowAny,]