from django.urls import path
from . import views

urlpatterns = [
    path("", views.ServiceListCreateView.as_view()),
    path("<int:pk>/", views.ServiceDetailView.as_view()),
    path("<int:pk>/agents/", views.service_agents),
    path("<int:pk>/assign-agents/", views.assign_agents),
    path("popular/", views.popular_services),
]
