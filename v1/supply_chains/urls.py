from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

router = DefaultRouter()
router.register('companies', views.CompanyViewSet, basename='companies')
router.register('farmers', views.FarmerViewSet, basename='farmers')
router.register('batches', views.BatchViewSet, basename='batches')

urlpatterns = [
    path('user-details/', views.UserDetailView.as_view()),
]

urlpatterns += router.urls