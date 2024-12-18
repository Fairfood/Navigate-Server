from django.urls import path
from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

router = DefaultRouter()
router.register('companies', views.CompanyViewSet, basename='companies')
router.register('farmers', views.FarmerViewSet, basename='farmers')
router.register('batches', views.BatchViewSet, basename='batches')


urlpatterns = [
    path('user/search/<str:email>/', views.UserSearchByEmailView.as_view(), name='user_search'),
    path('user/<str:pk>/', views.UserDetailsView.as_view(), name='user_details'),
]
urlpatterns += router.urls