from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RequestLogViewSet

router = DefaultRouter()
router.register(r'logs', RequestLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]