import django_filters

from .models import Service


class ServiceFilter(django_filters.FilterSet):
    """Filtros avanzados para servicios (S5).

    - name__icontains: filtra por nombre (case-insensitive).
    - estimated_time__lte: filtra por duración estimada máxima.
    - category: filtra por categoría exacta.
    """

    name__icontains = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
    )
    estimated_time__lte = django_filters.NumberFilter(
        field_name="estimated_time",
        lookup_expr="lte",
    )
    category = django_filters.CharFilter(
        field_name="category",
        lookup_expr="exact",
    )

    class Meta:
        model = Service
        fields = ["name__icontains", "estimated_time__lte", "category"]