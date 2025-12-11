from rest_framework import serializers
from .models import QueueTicket

class QueueTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueueTicket
        fields = '__all__'
