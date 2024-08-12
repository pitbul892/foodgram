from django.urls import include, path
from rest_framework import routers
# from .views import UserViewSet

# router = routers.DefaultRouter()
# router.register('users', UserViewSet)
urlpatterns = [
    # path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]