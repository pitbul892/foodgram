from django.urls import include, path
from rest_framework import routers
from .views import AvatarAPIView

router = routers.DefaultRouter()
# router.register(r'avatar', User)
urlpatterns = [
    path('users/me/avatar/', AvatarAPIView.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]