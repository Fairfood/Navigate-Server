from base import serializers

from .models import Farm
from .models import FarmComment

class FarmSerializer(serializers.IDModelSerializer):
    """
    Serializer class for the Farm model.
    """
    class Meta:
        model = Farm
        fields = '__all__'

class FarmCommentSerializer(serializers.IDModelSerializer):
    """
    Serializer class for the FarmComment model.
    """
    class Meta:
        model = FarmComment
        fields = '__all__'

