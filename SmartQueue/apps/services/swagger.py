from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema


service_list_docs = extend_schema(
    summary="Listado de servicios",
    description="Lista servicios con filtros avanzados por nombre, duración y categoría.",
    parameters=[
        OpenApiParameter(
            name="name__icontains",
            description="Filtrar por nombre (icontains)",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="estimated_time__lte",
            description="Filtrar por duración estimada máxima (minutos)",
            required=False,
            type=int,
        ),
        OpenApiParameter(
            name="category",
            description="Filtrar por categoría (coincidencia exacta)",
            required=False,
            type=str,
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