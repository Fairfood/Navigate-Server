from importlib import import_module
from django.http import Http404
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from base import generics as views

from ..farms.constants import template_files

from .models import Theme
from .models import Intervention
from .serializers import ThemeSerializer
from .serializers import InterventionSerializer

class ThemeView(views.ListCreateAPIView):
    """
    A view for listing and creating Theme objects.
    """
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            instance = self.get_queryset().last()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class InterventionView(viewsets.ModelViewSet):
    """
    A view for performing CRUD operations on Intervention objects.
    """
    queryset = Intervention.objects.all()
    serializer_class = InterventionSerializer

    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of interventions based on the provided piller.

        Args:
            request (HttpRequest): The HTTP request object.
            args: Variable length argument list.
            kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A response containing the list of interventions.

        Raises:
            ValidationError: If the provided piller is invalid.
        """
        piller = request.query_params.get('piller')
        if not piller or piller not in template_files.keys():
            raise ValidationError('Please provide a valid piller.')
        response = super().list(request, *args, **kwargs)
        processor = import_module(template_files[piller])
        data = {
            "title": processor.INTERVENTIONS_TITTLE,
            "description": processor.INTERVENTIONS_DESCRIPTION,
            "interventions": response.data.get("results")
        }
        return Response(data)
        
