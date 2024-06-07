from base import serializers
from rest_framework import serializers as base_serializers
from .models import Farm
from .models import FarmComment
from ..supply_chains.models.nodes import Farmer
from scripts import load_dummy_data

class FarmSerializer(serializers.IDModelSerializer):
    """
    Serializer class for the Farm model.
    """
    farmer = base_serializers.PrimaryKeyRelatedField(
        queryset=Farmer.objects.all(), required=False)

    class Meta:
        model = Farm
        fields = '__all__'

    def create(self, validated_data):
        """
        Create a new Farm instance.

        Args:
            validated_data (dict): The validated data for creating the Farm.

        Returns:
            Farm: The newly created Farm instance.
        """
        instance = super().create(validated_data)
        load_dummy_data.create_farm_properties(instance)
        load_dummy_data.create_deforestation_summery(instance)
        return instance


class FarmCommentSerializer(serializers.IDModelSerializer):
    """
    Serializer class for the FarmComment model.
    """
    class Meta:
        model = FarmComment
        fields = '__all__'

