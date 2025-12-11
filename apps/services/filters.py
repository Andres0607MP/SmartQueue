import django_filters
from .models import Service

class ServiceFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    category = django_filters.CharFilter(lookup_expr="icontains")
    min_time = django_filters.NumberFilter(field_name="estimated_time", lookup_expr="gte")
    max_time = django_filters.NumberFilter(field_name="estimated_time", lookup_expr="lte")

    class Meta:
        model = Service
        fields = ["name", "category", "min_time", "max_time"]
