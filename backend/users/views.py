from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser import views
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from rest_framework.pagination import LimitOffsetPagination
from .models import Subscriptions
from .serializers import UserSerializer, AvatarSerializer, SubscribeSerializer, SubscribtionSerializer

User = get_user_model()


class UserViewSet(views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
   

    @action(
        methods=[
            'get',
        ],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(
        methods=['put', 'delete'],
        url_path='me/avatar',
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = AvatarSerializer(request.user, data=request.data, partial=True)

            if serializer.is_valid():
                if 'avatar' in request.data:
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=[
            'post',
        ],
        # url_path='subscribe',
        detail=True,
        # permission_classes=[IsAuthenticated,]
    )
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        if self.request.method == "POST":
            serializer = SubscribeSerializer(
                data={'subscriber': author.id, 'user': user.id},
                context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = SubscribtionSerializer(
                author, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # subscription = Subscriptions.objects.filter(
        #     user=request.user, author=id)
        # if subscription.exists():
        #     subscription.delete()
        #     return Response(status=status.HTTP_204_NO_CONTENT)
        # return Response(
        #     {'error': 'Нет подписки для удаления.'},
        #     status=status.HTTP_400_BAD_REQUEST)
