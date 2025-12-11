from django.urls import path
from apps.smartqueue.views import simulate_assignment, commit_assignment

urlpatterns = [
    path('simulate/', simulate_assignment, name='simulate-assignment'),
    path('commit/', commit_assignment, name='commit-assignment'),
]
