from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth.models import User
from apps.queue_app.models import QueueTicket
from apps.services.models import Service
from apps.smartqueue import views as smart_views
from apps.users.serializers import RegisterSerializer
from apps.users.permissions import IsAdmin, IsAgent
from django.utils import timezone
from datetime import timedelta


class AssignmentTests(TestCase):
	def setUp(self):
		# Caller (any authenticated user) and one agent
		self.caller = User.objects.create_user(username='caller', password='pass')
		self.agent = User.objects.create_user(username='agent1', password='pass')
		# Ensure profile exists (signals create it) and set role
		self.agent.profile.role = 'agent'
		self.agent.profile.save()

		# Service and assign agent
		self.service = Service.objects.create(name='Atencion', description='x', estimated_time=10, category='general')
		self.service.agents.add(self.agent)

		# Create a pending ticket for the service
		self.ticket = QueueTicket.objects.create(
			usuario=self.caller,
			servicio=self.service.name,
			numero_turno=1,
			prioridad=1,
			estado='PENDIENTE',
			hora_estimada=(timezone.now() + timedelta(hours=1))
		)

		self.factory = APIRequestFactory()

	def test_simulate_assignment_returns_assignment(self):
		request = self.factory.post('/fake/')
		force_authenticate(request, user=self.caller)
		response = smart_views.simulate_assignment(request)
		self.assertEqual(response.status_code, 200)
		data = response.data
		self.assertEqual(data.get('mode'), 'simulate')
		self.assertTrue(isinstance(data.get('assignments'), list))
		self.assertEqual(data['assignments'][0]['ticket_id'], self.ticket.id)

	def test_commit_assignment_commits_and_sets_ticket(self):
		request = self.factory.post('/fake/')
		force_authenticate(request, user=self.caller)
		response = smart_views.commit_assignment(request)
		self.assertEqual(response.status_code, 200)
		self.ticket.refresh_from_db()
		self.assertEqual(self.ticket.estado, 'EN_CURSO')
		# usuario should be set to an agent
		self.assertEqual(self.ticket.usuario.id, self.agent.id)

	def test_commit_assignment_handles_error_and_rolls_back(self):
		# Monkeypatch assign_tickets to return an assignment with invalid agent id
		original_assign = smart_views.assign_tickets
		try:
			fake_assignment = [{
				'ticket_id': self.ticket.id,
				'service_id': self.service.id,
				'agent_id': 999999,  # non-existent
				'estimated_start': timezone.now().isoformat(),
			}]

			smart_views.assign_tickets = lambda: fake_assignment

			request = self.factory.post('/fake/')
			force_authenticate(request, user=self.caller)
			response = smart_views.commit_assignment(request)
			self.assertEqual(response.status_code, 500)

			# ensure ticket state was not changed
			self.ticket.refresh_from_db()
			self.assertEqual(self.ticket.estado, 'PENDIENTE')
		finally:
			smart_views.assign_tickets = original_assign


class SerializerPermissionTests(TestCase):
	def test_register_serializer_creates_user_and_profile(self):
		data = {
			'username': 'newuser',
			'email': 'n@example.com',
			'password': 'secret123'
		}
		serializer = RegisterSerializer(data=data)
		self.assertTrue(serializer.is_valid(), serializer.errors)
		user = serializer.save()
		self.assertIsNotNone(user.id)
		# profile should be created by signal
		self.assertTrue(hasattr(user, 'profile'))

	def test_permissions_is_admin_and_is_agent(self):
		admin = User.objects.create_user(username='admin', password='p')
		admin.profile.role = 'admin'
		admin.profile.save()

		agent = User.objects.create_user(username='agentp', password='p')
		agent.profile.role = 'agent'
		agent.profile.save()

		# is_admin permission
		perm_admin = IsAdmin()
		self.assertTrue(perm_admin.has_permission(request=type('R', (), {'user': admin}), view=None))
		self.assertFalse(perm_admin.has_permission(request=type('R', (), {'user': agent}), view=None))

		# is_agent permission
		perm_agent = IsAgent()
		self.assertTrue(perm_agent.has_permission(request=type('R', (), {'user': agent}), view=None))
		self.assertFalse(perm_agent.has_permission(request=type('R', (), {'user': admin}), view=None))

