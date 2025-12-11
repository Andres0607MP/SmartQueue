
from django.contrib.auth.models import User
from rest_framework import generics, permissions, viewsets, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import RegisterSerializer, ProfileSerializer, UserDetailSerializer, UserSerializer
from .models import Profile
from .permissions import IsAdmin, IsOwnerOrReadOnly
from .filters import UserFilter


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('profile')
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['username', 'email']
    ordering_fields = ['username', 'email']

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAdmin]
        elif self.action in ['retrieve']:
            permission_classes = [IsOwnerOrReadOnly]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [p() for p in permission_classes]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return UserDetailSerializer
        return UserSerializer

    def perform_update(self, serializer):
        # ensure profile role is not changed by non-admins
        serializer.save()

    @action(detail=False, methods=['get'], permission_classes=[IsAdmin])
    def me(self, request):
        serializer = UserDetailSerializer(request.user, context={'request': request})
        return Response(serializer.data)
