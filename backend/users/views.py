from django.contrib.auth import get_user_model
from djoser import views
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Subscriptions
from .serializers import UserSerializer, AvatarSerializer, SubscribeSerializer

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
        subscriber = request.user
        user_obj = self.get_object()
        serializer = SubscribeSerializer

        if user_obj == subscriber:
            return Response(
                "Нельзя подписываться на самого себя",
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription, created = Subscriptions.objects.get_or_create(
            user=user_obj,
            subscriber=request.user
        )
        serializer = SubscribeSerializer(
            subscription,
            context={'request': request}
        )
        return Response(status=status.HTTP_201_CREATED)
