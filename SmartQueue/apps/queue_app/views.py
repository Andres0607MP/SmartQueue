from rest_framework import viewsets, permissions, serializers
from django_filters.rest_framework import DjangoFilterBackend
from .models import QueueTicket
from .serializers import QueueTicketSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class QueueTicketViewSet(viewsets.ModelViewSet):
    queryset = QueueTicket.objects.all()
    serializer_class = QueueTicketSerializer

    # solo usuarios autenticados
    permission_classes = [permissions.IsAuthenticated]

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

        estado = serializer.validated_data.get("estado", "PENDIENTE")
        serializer.save(usuario=usuario, estado=estado)

    @action(detail=False, methods=["post"], url_path="create-ticket")
    def create_ticket(self, request):
        usuario = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        servicio = serializer.validated_data.get("servicio")

        if QueueTicket.objects.filter(
            usuario=usuario,
            servicio=servicio,
            estado="PENDIENTE"
        ).exists():
            return Response(
                {"detalle": "Ya tienes un ticket pendiente para este servicio."},
                status=status.HTTP_400_BAD_REQUEST
            )

        estado = serializer.validated_data.get("estado", "PENDIENTE")
        ticket = serializer.save(usuario=usuario, estado=estado) 
        return Response(QueueTicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_ticket(self, request, pk=None):
        ticket = self.get_object()

        if ticket.estado in ["ATENDIDO", "FINALIZADO" ,"CANCELADO"]:
            return Response(
                {"detalle": "No puedes cancelar un ticket ya atendido, finalizado o cancelado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        ticket.estado = "CANCELADO"
        ticket.save()

        return Response({"detalle": "Ticket cancelado correctamente."})


    @action(detail=False, methods=["get"], url_path="user/history")
    def user_history(self, request):
        usuario = request.user
        tickets = QueueTicket.objects.filter(usuario=usuario).order_by("-hora_estimada")
        serializer = QueueTicketSerializer(tickets, many=True)
        return Response(serializer.data)


