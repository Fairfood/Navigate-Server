from rest_framework import serializers as base_serializers

from base import serializers
from v1.farms import tasks
from v1.farms.models import Farm, FarmComment
from v1.supply_chains.models.analysis import AnalysisQueue
from v1.supply_chains.models.nodes import Farmer

# from scripts import load_dummy_data



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
        AnalysisQueue.objects.create(farm=instance)
        return instance
    
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        AnalysisQueue.objects.create(farm=instance)
        return instance


class FarmCommentSerializer(serializers.IDModelSerializer):
    """
    Serializer class for the FarmComment model.
    """
    class Meta:
        model = FarmComment
        fields = '__all__'

