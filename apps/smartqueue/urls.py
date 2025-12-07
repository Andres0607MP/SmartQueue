from django.urls import path

from . import views


urlpatterns = [
    path("simulate/", views.simulate_assignment, name="smart-simulate"),
    path("commit/", views.commit_assignment, name="smart-commit"),
]
