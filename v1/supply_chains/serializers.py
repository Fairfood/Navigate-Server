from django.db import transaction
from rest_framework import serializers

from base.fields import SerializableRelatedField
from base.serializers import IDModelSerializer
from base.session import get_current_company

from ..farms.models import Farm
from ..farms.serializers import FarmSerializer
from v1.dashboard.models import Theme
from .models.accounts import User
from .models.batches import Batch
from .models.nodes import Company, Farmer, SupplyChain
from .models.analysis import AnalysisQueue
from .constants import SyncStatus


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
        Returns the countries of the farmer plots associated with the company.
        """
        return Farm.objects.filter(
            farmer__in=obj.farmers.all()).values_list(
                'country', flat=True).distinct()


class FarmerSerializer(IDModelSerializer):
    """
    Serializer class for the Farmer model.
    """
    farms = FarmSerializer(many=True)
    supply_chain_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Farmer
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        farms = validated_data.pop('farms', [])
        supply_chain = self._get_supply_chain(validated_data)
        instance = super().create(validated_data)
        for farm in farms:
            farm['farmer'] = instance
        if farms:
            self.fields["farms"].create(farms)
        if supply_chain:
            instance.add_supply_chain(supply_chain)
        return instance
    
    @transaction.atomic
    def update(self, instance, validated_data):
        farms = validated_data.pop('farms', [])
        supply_chain = self._get_supply_chain(validated_data)
        instance = super().update(instance, validated_data)
        for farm in farms:
            farm['farmer'] = instance
        if farms:
            self.fields["farms"].create(farms)
        if supply_chain:
            instance.add_supply_chain(supply_chain)
        return instance
    
    def _get_supply_chain(self, validated_data):
        """
        Returns the supply chain instance.
        """
        supply_chain_name = validated_data.pop('supply_chain_name', None)
        if supply_chain_name:
            instance, _ = SupplyChain.objects.get_or_create(
                name=supply_chain_name)
            return instance
        return None


class BatchSerializer(IDModelSerializer):
    """
    Serializer class for the Batch model.
    """
    name = serializers.CharField(source='external_id', read_only=True)
    supply_chain_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Batch
        fields = '__all__'

    def validate(self, attrs):
        attrs['supply_chain'] = self.__get_supply_chain(attrs)
        return super().validate(attrs)
    
    def __get_supply_chain(self, attrs):
        """
        Returns the supply chain instance.
        """
        supply_chain_name = attrs.pop('supply_chain_name', None)
        if supply_chain_name:
            instance, _ = SupplyChain.objects.get_or_create(
                name=supply_chain_name)
            return instance
        return None

class UserSerializer(serializers.ModelSerializer):
    id = SerializableRelatedField(read_only=True)
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email',)


class BasicCompanySerializer(IDModelSerializer):
    """Basic serializer for company"""

    class Meta:
        model = Company
        fields = ['id', 'name', 'image']


class UserInfoSerializer(IDModelSerializer):
    """Serializer class to get user details"""

    default_company = serializers.SerializerMethodField()
    companies = BasicCompanySerializer(many=True, read_only=True)
    theme = serializers.SerializerMethodField()
    calculated_farms = serializers.SerializerMethodField()
    total_farms = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 
            'profile_image', 'sso_id', 'default_company', 'companies', 
            'theme', 'calculated_farms', 'total_farms'
        ]

    def get_default_company(self, obj):
        """Get default company"""

        company = get_current_company()
        return company.id
    
    def get_theme(self, obj):
        """Get company theme"""
        
        theme = Theme.objects.filter(company=get_current_company()).first()
        if not theme:
            theme = Theme.objects.filter(public_theme=True).last()
        return theme.id
    
    def get_calculated_farms(self, obj):
        """
        Get calculated farms. ie, farms whose yearly tree cover loss is 
        calculated.
        """

        farm_count = Farm.objects.filter(
            farmer__company=get_current_company(),
            analysis_queue__status=SyncStatus.COMPLETED).count()
        return farm_count

    def get_total_farms(self, obj):
        """
        Get total farms under the company
        """

        farm_count = Farm.objects.filter(
            farmer__company=get_current_company()).count()
        return farm_count