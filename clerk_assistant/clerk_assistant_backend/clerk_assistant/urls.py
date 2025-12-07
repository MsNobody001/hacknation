from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentTypeViewSet, AnalysisViewSet

router = DefaultRouter()
router.register(r'document-types', DocumentTypeViewSet, basename='documenttype')
router.register(r'analyses', AnalysisViewSet, basename='analysis')

urlpatterns = [
    path('', include(router.urls)),
]
