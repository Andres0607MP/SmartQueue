from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.services.models import Service


User = get_user_model()


class ServiceAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="admin123",
        )
        self.admin.is_staff = True
        self.admin.save()

        self.user = User.objects.create_user(
            username="user",
            email="user@test.com",
            password="user123",
        )

    def test_list_services_with_filters(self):
        Service.objects.create(name="Asesoría", category="general", estimated_time=10)
        Service.objects.create(name="Caja rápida", category="banco", estimated_time=5)

        self.client.force_authenticate(self.user)
        response = self.client.get("/api/services/?name=caja")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Caja rápida")

    def test_admin_can_create_service(self):
        self.client.force_authenticate(self.admin)
        payload = {
            "name": "Atención preferencial",
            "description": "Servicio rápido",
            "estimated_time": 15,
            "category": "banco",
        }
        response = self.client.post("/api/services/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Service.objects.count(), 1)
        self.assertEqual(Service.objects.first().name, "Atención preferencial")

    def test_non_admin_cannot_create_service(self):
        self.client.force_authenticate(self.user)
        payload = {
            "name": "Atención normal",
            "description": "Servicio",
            "estimated_time": 20,
            "category": "general",
        }
        response = self.client.post("/api/services/", payload, format="json")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Service.objects.count(), 0)

    def test_popular_services_endpoint(self):
        Service.objects.create(name="Servicio A", category="general", estimated_time=10)
        Service.objects.create(name="Servicio B", category="banco", estimated_time=5)

        self.client.force_authenticate(self.user)
        response = self.client.get("/api/services/popular/")

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 2)