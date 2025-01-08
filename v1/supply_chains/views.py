from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from base import session
from base.request_handler import CustomScopeViewset

from .models.accounts import User
from .models.batches import Batch
from .models.nodes import Company, Farmer, SupplyChain
from .serializers import (BatchSerializer, CompanySerializer, FarmerSerializer,
                          SupplyChainSerializer, UserSerializer, UserInfoSerializer)


class CompanyViewSet(CustomScopeViewset):
    """
    A viewset for managing Company objects.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    resource_types = ['company']

    def get_queryset(self):
        """
        Returns the queryset for the view.

        This method is responsible for filtering the queryset based on the 
        current user.

        Returns:
            QuerySet: The filtered queryset.
        """
        queryset = super().get_queryset()
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            return queryset.filter(users=self.request.user)
        return queryset

    @action(detail=True, methods=['post'], url_path='add-supply-chain')
    def add_supply_chain(self, request, *args, **kwargs):
        """
        Adds a supply chain to the instance.

        Args:
            request: The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A Response object with a success message and HTTP status code 201 
            (Created).
        """
        supply_chain = self.get_supply_chain(request)
        instance = self.get_object()
        instance.supply_chains.add(supply_chain)
        return Response('Added supply chain', status=status.HTTP_201_CREATED)
    
    @action(methods=['post'], detail=True, url_path='add-user')
    def add_user(self, request, *args, **kwargs):
        """
        Adds a user to the company.

        Args:
            request: The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A Response object with a success message and HTTP status code 201 
            (Created).
        """
        user = self.get_user(request)
        instance = self.get_object()
        instance.users.add(user)
        return Response('Added user', status=status.HTTP_201_CREATED)
    
    def get_user(self, request):
        """
        Retrieves a user based on the provided email.
        
        Args:
            request (Request): The HTTP request object.
        
        Returns:
            User: The retrieved user object.
        
        Raises:
            ValidationError: If the request data is invalid.
        """
        email = request.data.get("email")
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return User.objects.create(**request.data)
    
    def get_supply_chain(self, request):
        """
        Retrieves a supply chain based on the provided name.
        
        Args:
            request (Request): The HTTP request object.
        
        Returns:
            SupplyChain: The retrieved or created supply chain object.
        
        Raises:
            ValidationError: If the request data is invalid.
        """
        supply_chain_name = request.data.get("name")
        try:
            return SupplyChain.objects.get(name__iexact=supply_chain_name)
        except SupplyChain.DoesNotExist:
            serializer = SupplyChainSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return serializer.save()


class FarmerViewSet(CustomScopeViewset):
    """
    A viewset for managing Farmer objects.
    """
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer
    # et_fields = ('company',)
    resource_types = ['farmer']

    @action(methods=['post'], detail=False, url_path='bulk-create')
    def bulk_create(self, request):
        """
        API to create bulk uploads
        """
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response('Data created.', status=status.HTTP_201_CREATED)


class UserDetailsView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    resource_types = ['user']


class UserSearchByEmailView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'email'
    resource_types = ['user']


class BatchViewSet(CustomScopeViewset):
    """
    A viewset for managing Batch objects.
    """
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    resource_types = ['batch']

    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of supply chains filtered by the current request 
        and company.

        Args:
            request (HttpRequest): The current request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            list: A list of supply chains filtered by the current request and 
            company.
        """
        # Filter the queryset by the current request
        self.queryset = self.queryset.filter_by_request(request)
        
        # Get the current company
        company = session.get_current_company()
        
        # Filter the queryset by the company and make it distinct
        self.queryset = self.queryset.filter(
            farmers__company=company).distinct()
        
        # Call the list method of the superclass and return the result
        return super().list(request, *args, **kwargs)

class UserInfoView(APIView):
    """View to return user detials."""

    serializer_class = UserInfoSerializer

    def get(self, request, *args, **kwargs):
        """
        Override get method to get user from request and return user 
        details.
        """

        user = request.user
        serialized_data = self.serializer_class(
            user, context={'request': request}).data
        return Response(serialized_data, status=status.HTTP_200_OK)