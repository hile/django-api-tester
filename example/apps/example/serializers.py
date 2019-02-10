
from django.apps import apps
from rest_framework import serializers

from .validators import ExampleValidatior, ExampleUUIDValidatior


class ExampleBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for examples

    Example how to use the validator callback in apps.examples.validators
    """

    def validate(self, attrs):
        return ExampleValidatior(attrs).validate()


class ExampleListSerializer(ExampleBaseSerializer):
    """
    List serializer for example model
    """

    class Meta:
        model = apps.get_model('example', 'Example')
        fields = (
            'id',
            'label',
        )


class ExampleDetailsSerializer(ExampleBaseSerializer):
    """
    Details serializer for example model
    """

    class Meta:
        model = apps.get_model('example', 'Example')
        fields = (
            'label',
            'details',
        )


class ExampleUUIDBaseSerializer(serializers.HyperlinkedModelSerializer):
    """
    Base serializer for UUID hyperlinked examples
    """

    # Example how to link to namespace, view basename and detail route when the
    # view has custom lookup_field (see also views.py and urls.py)
    uuid = serializers.HyperlinkedIdentityField(
        lookup_field='uuid',
        view_name='example:example-uuid-detail'
    )

    def validate(self, attrs):
        """
        Example how to use the validator callback in apps.examples.validators
        """
        return ExampleUUIDValidatior(attrs).validate()


class ExampleUUIDListSerializer(ExampleUUIDBaseSerializer):
    """
    List serializer for UUID primary key linked examples
    """

    class Meta:
        model = apps.get_model('example', 'ExampleUUID')
        fields = (
            'uuid',
            'label',
        )


class ExampleUUIDDetailsSerializer(ExampleUUIDBaseSerializer):
    """
    Details serializer for UUID primary key linked examples
    """

    class Meta:
        model = apps.get_model('example', 'ExampleUUID')
        fields = (
            'label',
            'created',
            'details',
        )
