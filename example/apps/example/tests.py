
from django.urls import reverse

from django_api_tester.testcase import APITestCase, ModelTestCase, SerializerTestCase

from apps.example.models import Example, ExampleUUID
from apps.example.serializers import (
    ExampleListSerializer,
    ExampleDetailsSerializer,
    ExampleUUIDListSerializer,
    ExampleUUIDDetailsSerializer
)


class ExampleTestCase:
    """
    Commom base class for example.Example model testing

    Links the testcase to the model and creates a single record for tests
    """

    model = Example

    def setUp(self):
        super().setUp()
        self.model.objects.create(
            label='test record',
        )


class ExampleModelTestCase(ExampleTestCase, ModelTestCase):
    """
    Model tests for example.Example model
    """

    serializer_class = ExampleDetailsSerializer

    def test_model_example_create_record(self):
        """
        Test creating an item with serializer
        """

        self.create_valid_record(
            dict(
                label='test label'
            )
        )

    def test_model_example_create_validation_error(self):
        self.assertInvalidRecordValidationError(
            dict(
                label=''
            )
        )


class ExampleAPITestCase(ExampleTestCase, APITestCase):
    """
    Example API tests for example.Example model
    """

    def test_api_example_uuid_as_anonymous_list(self):
        """
        Test listing records in public API
        """
        self.validate_public_api_listing(
            'example:example-list'
        )

class ExampleSerializerBaseTestCase(ExampleTestCase, SerializerTestCase):
    """
    Example serializer tests for example.Example model
    """


class ExampleListSerializerTestCase(ExampleSerializerBaseTestCase):
    """
    Example model list serializer testcase
    """

    serializer_class = ExampleListSerializer

    def test_serializer_example_list(self):
        self.validate_serializing_list_of_items_to_dict(
            self.model.objects.all(),
        )


class ExampleDetailsSerializerTestCase(ExampleSerializerBaseTestCase):
    """
    Example model details serializer testcase
    """

    serializer_class = ExampleDetailsSerializer



class ExampleUUIDTestCase:
    """
    Commom base class for example.ExampleUUID model testing

    Links the testcase to the model and creates a single record for tests
    """

    model = ExampleUUID

    def setUp(self):
        super().setUp()
        self.model.objects.create(
            label='test record',
        )


class ExampleUUIDModelTestCase(ExampleUUIDTestCase, ModelTestCase):
    """
    Example model tests for example.ExampleUUID model
    """

    serializer_class = ExampleUUIDDetailsSerializer

    def test_model_example_uuid_create_record(self):
        """
        Test creating an item with serializer
        """

        self.create_valid_record(
            dict(
                label='test label'
            )
        )


class ExampleUUIDAPITestCase(ExampleUUIDTestCase, APITestCase):
    """
    Example API tests for example.ExampleUUID model
    """

    def test_api_example_uuid_as_anonymous_list(self):
        """
        Test listing records in public API
        """
        self.validate_public_api_listing(
            'example:example-uuid-list'
        )


class ExampleUUIDSerializerBaseTestCase(ExampleUUIDTestCase, SerializerTestCase):
    """
    Example serializer tests for example.ExampleUUID model
    """

    def setUp(self):
        super().setUp()
        self.model.objects.create(
            label='test record',
        )

    @property
    def request(self):
        return self.get_mock_request(
            method='get',
            path=reverse('example:example-uuid-list'),
        )

class ExampleUUIDListSerializerTestCase(ExampleUUIDSerializerBaseTestCase):
    """
    ExampleUUID model list serializer testcase
    """

    serializer_class = ExampleUUIDListSerializer

    def test_serializer_example_uuid_list(self):
        self.validate_serializing_list_of_items_to_dict(
            self.model.objects.all(),
            context={'request': self.request},
        )


class ExampleUUIDDetailsSerializerTestCase(ExampleUUIDSerializerBaseTestCase):
    """
    ExampleUUID model details serializer testcase
    """

    serializer_class = ExampleUUIDDetailsSerializer

    def test_serializer_example_uuid_details(self):
        self.validate_serializing_list_of_items_to_dict(
            self.model.objects.all(),
            context={'request': self.request},
        )
