import importlib

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from base import session
from .models import Farm
from .models import FarmComment
from .serializers import FarmSerializer
from .serializers import FarmCommentSerializer
from .constants import Pillers
from .constants import template_files

class FarmViewSet(viewsets.ModelViewSet):
    """
    A viewset for handling CRUD operations on Farm objects.

    """

    queryset = Farm.objects.all()
    serializer_class = FarmSerializer

    def get_queryset(self):
        """
        Returns the filtered queryset based on the current request.

        Returns:
            QuerySet: The filtered queryset of Farm objects.

        """
        return super().get_queryset().filter_by_request(self.request)
    
    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of farms filtered by the current company.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponse: The HTTP response containing the list of farms.

        """
        company = session.get_current_company()
        self.queryset = self.queryset.filter(farmer__company=company)
        return super().list(request, *args, **kwargs)
    
    
    @action(methods=['get'], detail=False, url_path='geo-jsons')
    def geoj_sons(self, request):
        """
        Returns the geo_json values of the queryset.

        Args:
            request: The HTTP request object.

        Returns:
            A Response object containing the geo_json values of the queryset.
        """
        queryset = self.get_queryset()
        company = session.get_current_company()
        queryset = queryset.filter(farmer__company=company)
        data = queryset.values_list('geo_json', flat=True)
        return Response(data)
    
    @action(methods=['post'], detail=False, url_path='bulk-create')
    def bulk_create(self, request):
        """
        API to create bulk uploads
        """
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response('Data created.', status=status.HTTP_201_CREATED)


        
    
class FarmCommentViewSet(viewsets.ModelViewSet):
    """
    A viewset for handling CRUD operations on FarmComment objects.

    """

    queryset = FarmComment.objects.all()
    serializer_class = FarmCommentSerializer

    def get_queryset(self):
        """
        Returns the filtered queryset based on the current request.

        Returns:
            QuerySet: The filtered queryset of FarmComment objects.

        """
        return super().get_queryset().filter_by_request(self.request)
    
class StatAPIView(APIView):
    """
    API view for retrieving statistics data based on the provided 'piller' 
    parameter.
    """
    def get(self, request):
        """
        The 'piller' parameter is required and should be a valid value from 
        the Pillers.labels() list.

        This view filters the Farm objects based on the request and uses a 
        processor module to generate statistics data from the filtered 
        queryset.


        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: The HTTP response object.

        Raises:
            ValidationError: If 'piller' parameter is missing or invalid.

        """
        piller = request.GET.get('piller')
        if not piller:
            raise ValidationError("Piller is required.")
        if piller not in Pillers.values:
            raise ValidationError("Enter valid piller.")
        queryset = Farm.objects.filter_by_request(request)
        queryset = queryset.filter(
            farmer__company=session.get_current_company())
        proccessor = importlib.import_module(template_files[piller])
        return Response(proccessor.stats.get_data(queryset))

class AnalysisViewSet(viewsets.ViewSet):
    """
    A view for performing analysis on farms based on the provided 'piller' 
    parameter.

    This view expects a 'piller' parameter in the request query parameters. It 
    validates the parameter and performs analysis on farms based on the 
    provided 'piller' value.

    If the 'piller' parameter is not provided or is not a valid value, a 
    ValidationError is raised.

    The analysis is performed by dynamically importing a module based on the 
    'piller' value, and calling the 'get_data' method of the 'analysis' 
    attribute of the imported module.

    Returns:
        A Response object containing the analysis data.

    Raises:
        ValidationError: If the 'piller' parameter is not provided or is not a 
        valid value.
    """
    def list(self, request):
        """
        Handle GET requests.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: The HTTP response object.

        Raises:
            ValidationError: If 'piller' is not provided or is not a valid 
            piller.

        """
        piller = request.GET.get('piller')
        if not piller:
            raise ValidationError("Piller is required.")
        if piller not in Pillers.values:
            raise ValidationError("Enter valid piller.")
        queryset = Farm.objects.filter_by_request(request)
        queryset = queryset.filter(
            farmer__company=session.get_current_company())
        proccessor = importlib.import_module(template_files[piller])
        return Response(proccessor.analysis.get_data(queryset))
    
    @action(methods=['get'], detail=False, url_path='details')
    def details(self, request):
        """
        Returns the detail data of the queryset.

        Args:
            request: The HTTP request object.

        Returns:
            A Response object containing the detail data of the queryset.
        """
        piller = request.GET.get('piller')
        method = request.GET.get('method')
        criteria = request.GET.get('criteria', '')
        if not piller:
            raise ValidationError("Piller is required.")
        if piller not in Pillers.values:
            raise ValidationError("Enter valid piller.")
        queryset = Farm.objects.filter_by_request(request)
        queryset = queryset.filter(
            farmer__company=session.get_current_company())
        proccessor = importlib.import_module(template_files[piller])
        return Response(
            proccessor.analysis_detail.get_data(queryset, method, criteria))
    


        

