from rest_framework import viewsets
from base import generics as views

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

class InterventionView(viewsets.ModelViewSet):
    """
    A view for performing CRUD operations on Intervention objects.
    """
    queryset = Intervention.objects.all()
    serializer_class = InterventionSerializer