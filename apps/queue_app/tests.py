from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import QueueTicket
from datetime import timedelta
from django.utils import timezone

class QueueTicketTests(TestCase):
	def setUp(self):
		# Crear usuario y cliente API
		self.user = User.objects.create_user(username="testuser", password="password123")
		self.client = APIClient()
		self.client.force_authenticate(user=self.user)

		# Datos base para crear un ticket (sin 'estado')
		self.ticket_data = {
			"servicio": "Atención",
			"numero_turno": 1,
			"prioridad": 1,
			"hora_estimada": (timezone.now() + timedelta(hours=1)).isoformat(),
			"usuario": self.user.id
		}

	def test_create_ticket(self):
		"""Prueba creación de ticket"""
		response = self.client.post("/api/queue/tickets/create-ticket/", self.ticket_data, format='json')
		if response.status_code != status.HTTP_201_CREATED:
			print("\n[DEBUG] response.data:", response.data)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(QueueTicket.objects.count(), 1)
		ticket = QueueTicket.objects.first()
		self.assertEqual(ticket.estado, "PENDIENTE")  # Debe asignar por defecto

	def test_duplicate_ticket(self):
		"""Prueba que no se puede crear ticket pendiente duplicado"""
		self.client.post("/api/queue/tickets/create-ticket/", self.ticket_data, format='json')
		response = self.client.post("/api/queue/tickets/create-ticket/", self.ticket_data, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


	def test_cancel_ticket(self):
		"""Prueba cancelar ticket pendiente"""
		ticket_data_no_estado = self.ticket_data.copy()
		ticket = QueueTicket.objects.create(
			usuario=self.user,
			servicio=ticket_data_no_estado["servicio"],
			numero_turno=ticket_data_no_estado["numero_turno"],
			prioridad=ticket_data_no_estado["prioridad"],
			hora_estimada=ticket_data_no_estado["hora_estimada"],
			estado="PENDIENTE"
		)
		response = self.client.post(f"/api/queue/tickets/{ticket.id}/cancel/")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		ticket.refresh_from_db()
		self.assertEqual(ticket.estado, "CANCELADO")


	def test_cancel_ticket_atendido(self):
		"""Prueba que no se puede cancelar un ticket ya atendido"""
		ticket_data_no_estado = self.ticket_data.copy()
		ticket = QueueTicket.objects.create(
			usuario=self.user,
			servicio=ticket_data_no_estado["servicio"],
			numero_turno=ticket_data_no_estado["numero_turno"],
			prioridad=ticket_data_no_estado["prioridad"],
			hora_estimada=ticket_data_no_estado["hora_estimada"],
			estado="ATENDIDO"
		)
		response = self.client.post(f"/api/queue/tickets/{ticket.id}/cancel/")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


	def test_user_history(self):
		"""Prueba historial de tickets de usuario"""
		ticket_data_no_estado = self.ticket_data.copy()
		QueueTicket.objects.create(
			usuario=self.user,
			servicio=ticket_data_no_estado["servicio"],
			numero_turno=ticket_data_no_estado["numero_turno"],
			prioridad=ticket_data_no_estado["prioridad"],
			hora_estimada=ticket_data_no_estado["hora_estimada"],
			estado="PENDIENTE"
		)
		response = self.client.get("/api/queue/tickets/user/history/")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)

	def test_create_ticket_unauthenticated(self):
		"""Prueba que un usuario no autenticado no puede crear tickets"""
		self.client.force_authenticate(user=None)
		response = self.client.post("/api/queue/tickets/create-ticket/", self.ticket_data, format='json')
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


	def test_cancel_ticket_unauthenticated(self):
		"""Prueba que un usuario no autenticado no puede cancelar tickets"""
		ticket_data_no_estado = self.ticket_data.copy()
		ticket = QueueTicket.objects.create(
			usuario=self.user,
			servicio=ticket_data_no_estado["servicio"],
			numero_turno=ticket_data_no_estado["numero_turno"],
			prioridad=ticket_data_no_estado["prioridad"],
			hora_estimada=ticket_data_no_estado["hora_estimada"],
			estado="PENDIENTE"
		)
		self.client.force_authenticate(user=None)
		response = self.client.post(f"/api/queue/tickets/{ticket.id}/cancel/")
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_create_ticket_invalid_data(self):
		"""Prueba creación de ticket con datos inválidos"""
		invalid_data = self.ticket_data.copy()
		invalid_data.pop("servicio")  # Falta campo obligatorio
		response = self.client.post("/api/queue/tickets/create-ticket/", invalid_data, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)