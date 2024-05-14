from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('companies', views.CompanyViewSet, basename='companies')
router.register('farmers', views.FarmerViewSet, basename='farmers')
router.register('batches', views.FarmerViewSet, basename='batches')

urlpatterns = router.urls