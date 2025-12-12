from django.test import TestCase
from django.contrib.auth.models import User
from apps.queue_app.serializers import QueueTicketSerializer
from apps.queue_app.models import QueueTicket
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta


class QueueSerializerBusinessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='quser', password='p')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.ticket_data = {
            'usuario': self.user.id,
            'servicio': 'Caja',
            'numero_turno': 5,
            'prioridad': 2,
            'hora_estimada': (timezone.now() + timedelta(hours=2)).isoformat()
        }

    def test_queue_ticket_serializer_fields(self):
        ser = QueueTicketSerializer(data=self.ticket_data)
        self.assertTrue(ser.is_valid(), ser.errors)
        obj = ser.create(ser.validated_data)
        self.assertIsInstance(obj, QueueTicket)

    def test_perform_create_duplicate_block(self):
        # create one pending
        QueueTicket.objects.create(usuario=self.user, servicio='Caja', numero_turno=1, prioridad=1, hora_estimada=timezone.now()+timedelta(hours=1), estado='PENDIENTE')
        # attempt to create another via API endpoint path (use client)
        data = self.ticket_data.copy()
        resp = self.client.post('/api/queue/tickets/create-ticket/', data, format='json')
        self.assertEqual(resp.status_code, 400)
