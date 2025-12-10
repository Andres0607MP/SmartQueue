from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from users.models import Profile

from .filters import ServiceFilter
from .models import Service
from .serializers import (
    AgentSerializer,
    AssignAgentsSerializer,
    ServiceSerializer,
)
from .swagger import service_list_docs


# =========================================================
# LISTAR AGENTES DE UN SERVICIO  (GET /services/<id>/agents/)
# =========================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def service_agents(request, pk):
    """Lista los agentes (perfiles con rol 'agent') asignados a un servicio."""

    service = get_object_or_404(Service, pk=pk)

    # Users relacionados al servicio (User objects)
    users_qs = service.agents.all()

    # Perfiles de agentes (Profile objects con role="agent")
    profiles_qs = Profile.objects.filter(user__in=users_qs, role="agent")

    data = {
        "service": service.name,
        "agents": AgentSerializer(profiles_qs, many=True).data,
    }
    return Response(data, status=status.HTTP_200_OK)


# =========================================================
# ASIGNAR AGENTES A UN SERVICIO  (POST /services/<id>/assign-agents/)
# =========================================================
@api_view(["POST"])
@permission_classes([IsAdminUser])
def assign_agents(request, pk):
    """Asigna agentes (perfiles con rol 'agent') a un servicio."""

    service = get_object_or_404(Service, pk=pk)
    serializer = AssignAgentsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Lista de IDs de perfiles enviados
    profile_ids = serializer.validated_data["agents"]

    # Validamos que esos perfiles existan y sean agentes
    profiles_qs = Profile.objects.filter(id__in=profile_ids, role="agent")

    # Necesitamos IDs de usuarios para asignar al many-to-many del modelo Service
    user_ids = profiles_qs.values_list("user_id", flat=True)

    # Asignación final
    service.agents.set(user_ids)

    data = {
        "message": "Agentes asignados correctamente",
        "service": service.name,
        "agents": AgentSerializer(profiles_qs, many=True).data,
    }
    return Response(data, status=status.HTTP_200_OK)


# =========================================================
# LISTAR Y CREAR SERVICIOS (GET/POST /services/)
# =========================================================
class ServiceListCreateView(generics.ListCreateAPIView):
    """Vista de lista/creación de servicios con documentación Swagger."""

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ServiceFilter

    @service_list_docs
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
