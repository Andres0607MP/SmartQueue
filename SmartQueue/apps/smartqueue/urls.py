from django.urls import path
from apps.services.views import (
    service_agents,
    assign_agents,
    ServiceListCreateView,
    ServiceDetailView,
)

urlpatterns = [
    # CRUD de servicios (S3)
    path("services/", ServiceListCreateView.as_view(), name="service-list"),
    path("services/<int:pk>/", ServiceDetailView.as_view(), name="service-detail"),

    # Endpoints personalizados (S2)
    path("services/<int:pk>/agents/", service_agents, name="service-agents"),
    path("services/<int:pk>/assign-agents/", assign_agents, name="assign-agents"),
]
