from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Service
from .serializers import AssignAgentsSerializer, ServiceSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def service_agents(request, pk):
    service = get_object_or_404(Service, pk=pk)
    return Response({
        "service": service.name,
        "agents": [
            {"id": a.id, "username": a.username, "email": a.email}
            for a in service.agents.all()
        ]
    })


@api_view(["POST"])
@permission_classes([IsAdminUser])
def assign_agents(request, pk):
    service = get_object_or_404(Service, pk=pk)
    serializer = AssignAgentsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    service.agents.set(serializer.validated_data["agent_ids"])
    return Response({"message": "Agentes asignados correctamente"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def popular_services(request):
    popular = Service.objects.order_by("-estimated_time")[:5]
    return Response(ServiceSerializer(popular, many=True).data)
class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = ServiceFilter
class ServiceListCreateView(generics.ListCreateAPIView):
    """
    get:
        Lista todos los servicios con filtros avanzados.

    post:
        Crea un nuevo servicio.
    """
