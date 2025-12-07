from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def simulate_assignment(request):
	data = {
		"status": "ok",
		"mode": "simulate",
		"assignments": [
			{
				"ticket_id": 1,
				"service_id": 1,
				"agent_id": 1,
				"estimated_start": "2025-01-01T10:00:00Z",
			}
		],
	}
	return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def commit_assignment(request):
	data = {
		"status": "ok",
		"mode": "commit",
		"committed": True,
	}
	return Response(data, status=status.HTTP_200_OK)

