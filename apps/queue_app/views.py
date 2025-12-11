from rest_framework import viewsets, permissions, serializers
from django_filters.rest_framework import DjangoFilterBackend
from .models import QueueTicket
from .serializers import QueueTicketSerializer

class QueueTicketViewSet(viewsets.ModelViewSet):
    queryset = QueueTicket.objects.all()
    serializer_class = QueueTicketSerializer

    # solo usuarios autenticados
    permission_classes = [permissions.IsAuthenticated]

    # filtros habilitados usando django-filter
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "servicio": ["exact"],
        "prioridad": ["exact"],
        "estado": ["exact"],
        "hora_estimada": ["gte", "lte"],
    }

    def perform_create(self, serializer):
        usuario = self.request.user
        servicio = serializer.validated_data.get("servicio")

        # evita duplicado del mismo tickwet activo
        if QueueTicket.objects.filter(
            usuario=usuario,
            servicio=servicio,
            estado="PENDIENTE"   # estado en este momento
        ).exists():
            raise serializers.ValidationError(
                {"detalle": "Ya tienes un ticket pendiente para este servicio."}
            )

        serializer.save(usuario=usuario)
