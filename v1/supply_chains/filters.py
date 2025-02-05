from django_filters import rest_framework as filters

from .models.accounts import User


class UserFilterSet(filters.FilterSet):
    """A filter set for the User model.

    This filter set allows filtering of User objects.
    """

    email = filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = User
        fields = ("email",)