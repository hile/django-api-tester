
from uuid import uuid4

from django.db import models
from django.utils import timezone


class Example(models.Model):
    """
    Example model
    """

    label = models.CharField(max_length=128)
    details = models.TextField(null=True, default=None)

    class Meta:
        ordering = ['label']

    def __str__(self):
        return self.label


class ExampleUUID(models.Model):
    """
    Example model with UUID primary key and automatic create timestamp
    """

    uuid = models.UUIDField(default=uuid4, editable=False, primary_key=True)

    created = models.DateTimeField(default=timezone.now)

    label = models.CharField(max_length=128)
    details = models.TextField(null=True, default=None)

    class Meta:
        ordering = ['created', 'label']

    def __str__(self):
        return self.label
