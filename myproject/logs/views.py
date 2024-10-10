from rest_framework import viewsets
from .models import RequestLog
from .serializers import RequestLogSerializer

class RequestLogViewSet(viewsets.ModelViewSet):
    queryset = RequestLog.objects.all()
    serializer_class = RequestLogSerializer

