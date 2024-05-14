from rest_framework import serializers
from base.serializers import IDModelSerializer

from .models.nodes import Company, Farmer, SupplyChain
from .models.batches import Batch

class SupplyChainSerializer(IDModelSerializer):
    """
    
    """
    class Meta:
        model = SupplyChain
        fields = '__all__'

class CompanySerializer(IDModelSerializer):
    """
    Serializer class for the Company model.
    """
    
    farmer_countries = serializers.SerializerMethodField()
    supply_chains = SupplyChainSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        exclude = ('users',)

    def get_farmer_countries(self, obj):
        """
        Returns the countries of the farmers associated with the company.
        """
        return obj.farmers.values_list('country', flat=True).distinct()


class FarmerSerializer(IDModelSerializer):
    """
    Serializer class for the Farmer model.
    """
    class Meta:
        model = Farmer
        fields = '__all__'


class BatchSerializer(IDModelSerializer):
    """
    Serializer class for the Batch model.
    """
    class Meta:
        model = Batch
        fields = '__all__'