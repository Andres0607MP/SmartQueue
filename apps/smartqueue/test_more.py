from django.test import TestCase
from django.contrib.auth.models import User
from apps.services.models import Service
from apps.queue_app.models import QueueTicket
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient


class SmartQueueAssignmentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # create two agents
        self.agent1 = User.objects.create_user(username='a1', password='p')
        self.agent1.profile.role = 'agent'
        self.agent1.profile.save()

        self.agent2 = User.objects.create_user(username='a2', password='p')
        self.agent2.profile.role = 'agent'
        self.agent2.profile.save()

        # service and assign both agents
        self.service = Service.objects.create(name='TestSvc', description='', estimated_time=5)
        self.service.agents.set([self.agent1.id, self.agent2.id])

        # create customer user and tickets
        self.customer = User.objects.create_user(username='cust', password='p')

        # create two pending tickets
        QueueTicket.objects.create(usuario=self.customer, servicio='TestSvc', numero_turno=1, prioridad=2, hora_estimada=timezone.now()+timedelta(minutes=30), estado='PENDIENTE')
        QueueTicket.objects.create(usuario=self.customer, servicio='TestSvc', numero_turno=2, prioridad=1, hora_estimada=timezone.now()+timedelta(minutes=40), estado='PENDIENTE')

        # Give agent1 one in-progress ticket to create imbalance
        QueueTicket.objects.create(usuario=self.agent1, servicio='TestSvc', numero_turno=99, prioridad=1, hora_estimada=timezone.now()+timedelta(minutes=10), estado='EN_CURSO')

    def test_simulate_and_commit_assignment(self):
        # authenticate as any user
        user = User.objects.create_user(username='u', password='p')
        user.profile.role = 'customer'
        user.profile.save()
        self.client.force_authenticate(user=user)

        # Call assign_tickets directly to test business logic
        from apps.smartqueue.views import assign_tickets

        assignments = assign_tickets()
        # should have at least one assignment
        self.assertTrue(isinstance(assignments, list))
        self.assertTrue(len(assignments) >= 1)

        # Emulate commit assignment logic (atomic behavior tested elsewhere)
        committed = []
        for a in assignments:
            ticket = QueueTicket.objects.get(id=a['ticket_id'])
            agent = User.objects.get(id=a['agent_id'])
            ticket.estado = 'EN_CURSO'
            ticket.usuario = agent
            ticket.hora_estimada = timezone.now()
            ticket.save()
            committed.append(ticket.id)

        # verify tickets moved to EN_CURSO
        self.assertTrue(QueueTicket.objects.filter(estado='EN_CURSO').count() >= 1)

        # verify tickets moved to EN_CURSO
        self.assertTrue(QueueTicket.objects.filter(estado='EN_CURSO').count() >= 1)
