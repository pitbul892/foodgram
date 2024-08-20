from django.urls import include, path
from rest_framework import routers
# from .views import AvatarAPIView
from .views import UserViewSet
router = routers.DefaultRouter()
router.register('users', UserViewSet)
# router.register('users/me/', UserViewSet, basename='me')
# router.register('users/me/avatar/', UserViewSet, basename='avatar')
urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]