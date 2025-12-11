from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    estimated_time = models.PositiveIntegerField()
    category = models.CharField(max_length=100, blank=True)

    agents = models.ManyToManyField(
        User,
        related_name="assigned_services",
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
