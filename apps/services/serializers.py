class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class ServiceSerializer(serializers.ModelSerializer):
    agents = AgentSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = [
            "id", "name", "description", "estimated_time",
            "category", "agents", "created_at"
        ]
class AssignAgentsSerializer(serializers.Serializer):
    agent_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
