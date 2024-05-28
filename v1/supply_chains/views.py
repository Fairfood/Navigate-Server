from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

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

    @action(methods=['post'], detail=False, url_path='bulk-create')
    def bulk_create(self, request):
        """
        API to create bulk uploads
        """
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response('Data created.', status=status.HTTP_201_CREATED)

class BatchViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing Batch objects.
    """
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer

    @action(methods=['post'], detail=False, url_path='bulk-create')
    def bulk_create(self, request):
        """
        API to create bulk uploads
        """
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response('Data created.', status=status.HTTP_201_CREATED)



