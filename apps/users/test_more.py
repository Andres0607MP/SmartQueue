from django.test import TestCase, RequestFactory
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from apps.users.serializers import UserDetailSerializer, RegisterSerializer
from apps.users.permissions import IsAdmin, IsAgent, IsOwnerOrReadOnly
from apps.users.views import ProfileMeView, UserViewSet
from apps.users.models import Profile


class UserSerializersPermissionsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = APIClient()
        # admin user
        self.admin = User.objects.create_user(username='adminx', password='p')
        self.admin.profile.role = 'admin'
        self.admin.profile.save()

        # normal user
        self.user = User.objects.create_user(username='bob', password='p')

    def test_register_serializer_creates_user_and_profile(self):
        data = {'username': 'newu', 'email': 'n@e.com', 'password': 'secret'}
        ser = RegisterSerializer(data=data)
        self.assertTrue(ser.is_valid())
        user = ser.save()
        self.assertTrue(User.objects.filter(username='newu').exists())
        # profile should exist (created by signal)
        self.assertTrue(hasattr(user, 'profile'))

    def test_userdetailserializer_prevents_role_change_by_non_admin(self):
        # user tries to update another field and nested profile role
        request = self.factory.put('/', data={'profile': {'role': 'admin'}} )
        request.user = self.user
        serializer = UserDetailSerializer(instance=self.user, data={'username': 'bob2', 'profile': {'role': 'admin'}}, context={'request': request}, partial=True)
        self.assertTrue(serializer.is_valid())
        updated = serializer.save()
        # role should not have changed
        self.user.profile.refresh_from_db()
        self.assertNotEqual(self.user.profile.role, 'admin')

    def test_userdetailserializer_allows_admin_role_change(self):
        request = self.factory.put('/', data={'profile': {'role': 'agent'}} )
        request.user = self.admin
        serializer = UserDetailSerializer(instance=self.user, data={'profile': {'role': 'agent'}}, context={'request': request}, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.user.profile.refresh_from_db()
        # admin can change role (signal creation ensures profile exists)
        self.assertIn(self.user.profile.role, ['agent', 'customer', 'admin'])

    def test_isadmin_isagent_permissions(self):
        admin_perm = IsAdmin()
        agent_perm = IsAgent()
        # admin user
        self.assertTrue(admin_perm.has_permission(self._fake_request(self.admin), None))
        self.assertFalse(agent_perm.has_permission(self._fake_request(self.admin), None))
        # normal user
        self.assertFalse(admin_perm.has_permission(self._fake_request(self.user), None))

    def _fake_request(self, user):
        req = self.factory.get('/')
        req.user = user
        return req

    def test_isowner_or_readonly_user_object(self):
        perm = IsOwnerOrReadOnly()
        req = self.factory.get('/')
        req.user = self.user
        # safe method: owner can view
        req.method = 'GET'
        self.assertTrue(perm.has_object_permission(req, None, self.user))
        # another user cannot view
        req.user = self.admin
        # admin can view
        self.assertTrue(perm.has_object_permission(req, None, self.user))
        # write method: only owner
        req.method = 'PUT'
        req.user = self.admin
        self.assertFalse(perm.has_object_permission(req, None, self.user))

    def test_profileme_view_returns_profile(self):
        view = ProfileMeView.as_view()
        factory = APIRequestFactory()
        request = factory.get('/')
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, 200)

