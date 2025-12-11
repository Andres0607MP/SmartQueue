from rest_framework import serializers
from apps.users.models import Profile
from .models import Service


# =========================================================
# SERIALIZER PARA MOSTRAR AGENTES (S2)
# =========================================================
class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "user", "role"]


# =========================================================
# SERIALIZER PARA ASIGNAR AGENTES A UN SERVICIO (S2)
# =========================================================
class AssignAgentsSerializer(serializers.Serializer):
    agents = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

    def validate_agents(self, value):
        agents = Profile.objects.filter(id__in=value, role="agent")
        if agents.count() != len(value):
            raise serializers.ValidationError(
                "Uno o más IDs no corresponden a perfiles con rol 'agent'."
            )
        return value


# =========================================================
# SERIALIZER PARA CRUD DE SERVICIOS (S3)
# =========================================================
class ServiceSerializer(serializers.ModelSerializer):
    """Serializer principal para CRUD de servicios."""

    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "description",
            "estimated_time",
            "category",
            "created_at",
        ]
