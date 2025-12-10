import django_filters
from .models import Service

class ServiceFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    category = django_filters.CharFilter(lookup_expr="icontains")
    duration_gte = django_filters.NumberFilter(field_name="estimated_duration", lookup_expr="gte")
    duration_lte = django_filters.NumberFilter(field_name="estimated_duration", lookup_expr="lte")

    class Meta:
        model = Service
        fields = ["name", "category"]
