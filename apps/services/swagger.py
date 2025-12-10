from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema


service_list_docs = extend_schema(
    summary="Listado de servicios",
    description="Lista servicios con filtros por nombre, categoría y duración.",
    parameters=[
        OpenApiParameter(
            name="name",
            description="Filtrar por nombre (icontains)",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="category",
            description="Filtrar por categoría (icontains)",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="duration_gte",
            description="Duración mínima (minutos)",
            required=False,
            type=int,
        ),
        OpenApiParameter(
            name="duration_lte",
            description="Duración máxima (minutos)",
            required=False,
            type=int,
        ),
    ],
)


popular_services_docs = extend_schema(
    summary="Servicios más populares",
    description="Devuelve una lista de servicios ordenados por popularidad (criterio definido por la implementación).",
    responses={200: OpenApiResponse(description="Lista de servicios populares.")},
)


service_agents_docs = extend_schema(
    summary="Agentes asignados a un servicio",
    description="Lista los agentes (perfiles con rol 'agent') asociados a un servicio específico.",
    responses={200: OpenApiResponse(description="Servicio y agentes asociados.")},
)