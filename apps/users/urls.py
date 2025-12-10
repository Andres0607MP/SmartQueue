
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, ProfileMeView, UserViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', ProfileMeView.as_view(), name='profile-me'),
    path('', include(router.urls)),
]
