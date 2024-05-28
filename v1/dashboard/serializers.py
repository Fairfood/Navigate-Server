from base import serializers
from .models import Intervention
from .models import Theme

class ThemeSerializer(serializers.IDModelSerializer):
    """
    Serializer for the Theme model.
    """
    class Meta:
        model = Theme
        fields = "__all__"

class InterventionSerializer(serializers.IDModelSerializer):
    """
    Serializer for the Intervention model.
    """
    class Meta:
        model = Intervention
        fields = "__all__"