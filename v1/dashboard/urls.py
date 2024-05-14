from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('interventions', 
                views.InterventionView, basename='interventions')

urlpatterns = [
    path('themes/', views.ThemeView.as_view(), name='themes'),
]

urlpatterns += router.urls