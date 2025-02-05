from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('farms', views.FarmViewSet, basename='farm')
router.register('farm-comments', views.FarmCommentViewSet, 
                basename='farm-comments')
router.register('analysis', views.AnalysisViewSet,basename='analysis')

urlpatterns = [
    path('stats/', views.StatAPIView.as_view(), name='stats'),
]

urlpatterns += router.urls