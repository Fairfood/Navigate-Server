import importlib

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

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
        if piller not in Pillers.labels():
            raise ValidationError("Enter valid piller.")
        queryset = Farm.objects.filter_by_request(request)
        proccessor = importlib.import_module(template_files[piller])
        return Response(proccessor.stats.get_data(queryset))

class AnalysisView(APIView):
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
    def get(self, request):
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
        if piller not in Pillers.labels():
            raise ValidationError("Enter valid piller.")
        queryset = Farm.objects.filter_by_request(request)
        proccessor = importlib.import_module(template_files[piller])
        return Response(proccessor.analysis.get_data(queryset))

        

