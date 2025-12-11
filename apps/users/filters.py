import django_filters
from django.contrib.auth.models import User


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    role = django_filters.CharFilter(field_name='profile__role', lookup_expr='exact')

    class Meta:
        model = User
        fields = ['username', 'email', 'role']
