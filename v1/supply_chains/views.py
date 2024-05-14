from rest_framework import viewsets
from .models.nodes import Company
from .models.nodes import Farmer
from .models.batches import Batch
from .serializers import CompanySerializer
from .serializers import FarmerSerializer
from .serializers import BatchSerializer

class CompanyViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing Company objects.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class FarmerViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing Farmer objects.
    """
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer

class BatchViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing Batch objects.
    """
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer



