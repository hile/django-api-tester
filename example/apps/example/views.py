
from django.apps import apps
from rest_framework import viewsets

from .serializers import (
    ExampleListSerializer,
    ExampleDetailsSerializer,
    ExampleUUIDListSerializer,
    ExampleUUIDDetailsSerializer
)


class ExampleViewSet(viewsets.ModelViewSet):
    """
    Model view set for simple example model
    """

    queryset = apps.get_model('example', 'Example').objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ExampleListSerializer
        else:
            return ExampleDetailsSerializer


class ExampleUUIDViewSet(viewsets.ModelViewSet):
    """
    Model view set for simple example model
    """

    lookup_field = 'uuid'
    queryset = apps.get_model('example', 'ExampleUUID').objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ExampleUUIDListSerializer
        else:
            return ExampleUUIDDetailsSerializer
