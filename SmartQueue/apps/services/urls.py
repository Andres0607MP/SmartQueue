from django.urls import path
from . import views

urlpatterns = [
    # Listar y crear servicios
    path("", views.ServiceListCreateView.as_view(), name="service-list"),
    
    # Servicios populares
    path("popular/", views.popular_services, name="popular-services"),
    
    # Obtener detalle de un servicio
    path("<int:pk>/", views.ServiceDetailView.as_view(), name="service-detail"),
    
    # Obtener agentes de un servicio
    path("<int:pk>/agents/", views.service_agents, name="service-agents"),
    
    # Asignar agentes a un servicio
    path("<int:pk>/assign-agents/", views.assign_agents, name="assign-agents"),
]
