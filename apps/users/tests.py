
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient


class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # create an admin user
        self.admin = User.objects.create_user(username='admin', password='pass')
        self.admin.profile.role = 'admin'
        self.admin.profile.save()

        # create a normal user
        self.user = User.objects.create_user(username='user', password='pass')

    def test_register(self):
        response = self.client.post('/api/users/register/', {
            'username': 'test',
            'email': 't@test.com',
            'password': '1234'
        }, format='json')
        self.assertEqual(response.status_code, 201)

    def test_me_profile_requires_auth(self):
        # unauthenticated should be 401
        resp = self.client.get('/api/users/me/')
        self.assertIn(resp.status_code, (401, 403))

    def test_admin_can_list_users(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get('/api/users/')
        self.assertEqual(resp.status_code, 200)

    def test_non_admin_cannot_list_users(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get('/api/users/')
        self.assertIn(resp.status_code, (403, 401))

    def test_filters_by_email_and_role(self):
        # create users with different emails and roles
        u1 = User.objects.create_user(username='alice', email='alice@example.com', password='p')
        u2 = User.objects.create_user(username='bob', email='bob@sample.com', password='p')
        u2.profile.role = 'agent'
        u2.profile.save()

        self.client.force_authenticate(user=self.admin)
        resp = self.client.get('/api/users/?email=alice@example.com')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # ensure at least one result and that email filtered
        self.assertTrue(any('alice@example.com' in (u.get('email') or '') for u in data))

        resp2 = self.client.get('/api/users/?role=agent')
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()
        self.assertTrue(len(data2) >= 1)
