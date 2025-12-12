from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response


from apps.users.models import Profile

from .filters import ServiceFilter
from .models import Service
from .serializers import (
    AgentSerializer,
    AssignAgentsSerializer,
    ServiceSerializer,
)
from .swagger import popular_services_docs, service_agents_docs, service_list_docs


class IsAdminOrReadOnly(permissions.BasePermission):
    """Solo admins pueden crear/editar/borrar; lectura para autenticados."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class ServiceViewSet(viewsets.ModelViewSet):
    """CRUD de servicios implementado como ViewSet para cumplir requisito.

    Endpoints adicionales implementados como acciones del ViewSet:
    - GET /services/popular/  -> popular services
    - GET /services/{pk}/agents/ -> list agents for service
    - POST /services/{pk}/assign_agents/ -> assign agents (admin only)
    """

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ServiceFilter

    @service_list_docs
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    @popular_services_docs
    def popular(self, request):
        services_qs = Service.objects.order_by("-created_at")[:10]
        data = ServiceSerializer(services_qs, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    @service_agents_docs
    def agents(self, request, pk=None):
        service = self.get_object()
        users_qs = service.agents.all()
        profiles_qs = Profile.objects.filter(user__in=users_qs, role="agent")

        data = {
            "service": service.name,
            "agents": AgentSerializer(profiles_qs, many=True).data,
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def assign_agents(self, request, pk=None):
        service = self.get_object()
        serializer = AssignAgentsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile_ids = serializer.validated_data["agents"]
        profiles_qs = Profile.objects.filter(id__in=profile_ids, role="agent")
        user_ids = profiles_qs.values_list("user_id", flat=True)

        service.agents.set(user_ids)

        data = {
            "message": "Agentes asignados correctamente",
            "service": service.name,
            "agents": AgentSerializer(profiles_qs, many=True).data,
        }
        return Response(data, status=status.HTTP_200_OK)