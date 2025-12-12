from django.test import TestCase
from django.contrib.auth.models import User
from apps.services.serializers import AssignAgentsSerializer
from apps.services.models import Service
from apps.users.models import Profile
from rest_framework.test import APIClient


class ServicesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # create admin user
        self.admin = User.objects.create_user(username='sadmin', password='p')
        self.admin.is_staff = True
        self.admin.save()
        self.admin.profile.role = 'admin'
        self.admin.profile.save()

        # create agent profiles
        self.agent1 = User.objects.create_user(username='agent1', password='p')
        self.agent1.profile.role = 'agent'
        self.agent1.profile.save()

        self.agent2 = User.objects.create_user(username='agent2', password='p')
        self.agent2.profile.role = 'agent'
        self.agent2.profile.save()

        # create a service
        self.service = Service.objects.create(name='CajaTest', description='desc', estimated_time=10)

    def test_assign_agents_serializer_validates_agents(self):
        # valid agents
        data = {'agents': [self.agent1.profile.id, self.agent2.profile.id]}
        ser = AssignAgentsSerializer(data=data)
        self.assertTrue(ser.is_valid(), ser.errors)

        # invalid agent id (non-agent)
        non_agent = User.objects.create_user(username='u', password='p')
        data2 = {'agents': [non_agent.profile.id, 9999]}
        ser2 = AssignAgentsSerializer(data=data2)
        self.assertFalse(ser2.is_valid())

    def test_popular_and_agents_and_assign_agents_endpoints(self):
        # popular requires authentication
        user = User.objects.create_user(username='u2', password='p')
        user.profile.role = 'customer'
        user.profile.save()
        self.client.force_authenticate(user=user)

        # create some services to populate popular
        for i in range(3):
            Service.objects.create(name=f'S{i}', description='', estimated_time=5)

        resp = self.client.get('/api/services/popular/')
        self.assertEqual(resp.status_code, 200)

        # agents list for service (no agents assigned yet)
        resp2 = self.client.get(f'/api/services/{self.service.id}/agents/')
        self.assertEqual(resp2.status_code, 200)
        self.assertIn('agents', resp2.json())

        # assign agents (admin only)
        self.client.force_authenticate(user=self.admin)
        assign_data = {'agents': [self.agent1.profile.id, self.agent2.profile.id]}
        resp3 = self.client.post(f'/api/services/{self.service.id}/assign_agents/', assign_data, format='json')
        self.assertEqual(resp3.status_code, 200)
        # service should have agents assigned
        self.service.refresh_from_db()
        self.assertTrue(self.service.agents.count() >= 2)
