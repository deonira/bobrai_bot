from rest_framework import generics, permissions, viewsets, status
from rest_framework.pagination import PageNumberPagination
from .models import RequestLog, UserSettings
from .serializers import RequestLogSerializer, UserSettingsSerializer
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework.response import Response
import uuid

class RequestLogPagination(PageNumberPagination):
    page_size = 10

class RequestLogFilter(filters.FilterSet):
    timestamp = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = RequestLog
        fields = ['timestamp']

class RequestLogList(viewsets.ModelViewSet):
    queryset = RequestLog.objects.all()
    serializer_class = RequestLogSerializer
    pagination_class = RequestLogPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = RequestLogFilter
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']

class RequestLogDetail(generics.RetrieveAPIView):
    queryset = RequestLog.objects.all()
    serializer_class = RequestLogSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return RequestLog.objects.filter(user_id=user_id)

class UserSettingsViewSet(viewsets.ModelViewSet):
    serializer_class = UserSettingsSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user_id = self.request.session.get('user_id')
        return UserSettings.objects.filter(user_id=user_id)

    def perform_create(self, serializer):
        user_id = self.request.session.get('user_id')
        if not user_id:
            user_id = str(uuid.uuid4())
            self.request.session['user_id'] = user_id

        serializer.save(user_id=user_id)

    def create(self, request, *args, **kwargs):
        user_settings, created = UserSettings.objects.update_or_create(
            user_id=self.request.session.get('user_id'),
            defaults=request.data
        )
        return Response(UserSettingsSerializer(user_settings).data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        user_id = self.request.session.get('user_id')
        instance = self.get_queryset().first()

        if not instance:
            return Response({'detail': 'Settings not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        settings = self.get_queryset().first()
        if settings:
            serializer = UserSettingsSerializer(settings)
            return Response(serializer.data)
        return Response({'detail': 'Settings not found.'}, status=status.HTTP_404_NOT_FOUND)