from django.db import models
from django.contrib.auth.models import User 

class QueueTicket(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_CURSO', 'En curso'),
        ('FINALIZADO', 'Finalizado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    servicio = models.CharField(max_length=100)
    numero_turno = models.IntegerField()
    prioridad = models.IntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    hora_estimada = models.DateTimeField()

    def __str__(self):
        return f"Turno {self.numero_turno} - {self.usuario.username}"
