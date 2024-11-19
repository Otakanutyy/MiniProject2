from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GradeViewSet

# Create a router and register the ViewSet
router = DefaultRouter()
router.register(r'', GradeViewSet, basename='grade')

urlpatterns = [
    path('', include(router.urls)),
]
