
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone

from apps.queue_app.models import QueueTicket
from apps.services.models import Service
from django.contrib.auth.models import User

def assign_tickets():
	# Obtener tickets pendientes ordenados por prioridad y número de turno
	tickets = list(QueueTicket.objects.filter(estado='PENDIENTE').order_by('-prioridad', 'numero_turno'))
	assignments = []
	agent_load = {}  # agente_id: cantidad de tickets asignados

	# Obtener todos los agentes y sus servicios
	agents = User.objects.filter(profile__role='agent')
	agent_services = {}
	for agent in agents:
		agent_services[agent.id] = set(agent.assigned_services.values_list('id', flat=True))
		agent_load[agent.id] = QueueTicket.objects.filter(estado='EN_CURSO', usuario=agent).count()

	for ticket in tickets:
		# Buscar agentes que pueden atender el servicio
		try:
			service = Service.objects.get(name=ticket.servicio)
		except Service.DoesNotExist:
			continue
		possible_agents = [a for a in agents if service.id in agent_services[a.id]]
		if not possible_agents:
			continue
		# Elegir el agente con menor carga
		agent = min(possible_agents, key=lambda a: agent_load[a.id])
		assignments.append({
			'ticket_id': ticket.id,
			'service_id': service.id,
			'agent_id': agent.id,
			'estimated_start': timezone.now().isoformat(),
		})
		agent_load[agent.id] += 1
	return assignments


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def simulate_assignment(request):
	assignments = assign_tickets()
	if not assignments:
		return Response({
			"status": "error",
			"detail": "No hay asignaciones posibles (sin agentes disponibles o tickets válidos)."
		}, status=status.HTTP_400_BAD_REQUEST)
	return Response({
		"status": "ok",
		"mode": "simulate",
		"assignments": assignments
	}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def commit_assignment(request):
	assignments = assign_tickets()
	if not assignments:
		return Response({
			"status": "error",
			"detail": "No hay asignaciones posibles (sin agentes disponibles o tickets válidos)."
		}, status=status.HTTP_400_BAD_REQUEST)

	for a in assignments:
		try:
			ticket = QueueTicket.objects.get(id=a['ticket_id'])
			agent = User.objects.get(id=a['agent_id'])
			ticket.estado = 'EN_CURSO'
			ticket.usuario = agent
			ticket.hora_estimada = timezone.now()
			ticket.save()
		except Exception as e:
			transaction.set_rollback(True)
			return Response({
				"status": "error",
				"detail": f"Error al asignar ticket {a['ticket_id']}: {str(e)}"
			}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	return Response({
		"status": "ok",
		"mode": "commit",
		"committed": True,
		"assignments": assignments
	}, status=status.HTTP_200_OK)

