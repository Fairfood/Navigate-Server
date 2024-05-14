from rest_framework import serializers

from .models.nodes import Company, Farmer
from .models.batches import Batch

class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer class for the Company model.
    """
    
    farmer_countries = serializers.SerializerMethodField()

    class Meta:
        model = Company
        exclude = ('users',)

    def get_farmer_countries(self, obj):
        """
        Returns the countries of the farmers associated with the company.
        """
        return obj.farmers.values_list('country', flat=True).distinct()


class FarmerSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Farmer model.
    """
    class Meta:
        model = Farmer
        fields = '__all__'


class BatchSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Batch model.
    """
    class Meta:
        model = Batch
        fields = '__all__'