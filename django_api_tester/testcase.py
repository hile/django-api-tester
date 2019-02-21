
import json
import pytest

from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.test import TestCase as DjangoTestCase
from django.urls import reverse
from django.test.client import RequestFactory

from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import ValidationError
from rest_framework.test import APITestCase as DRFAPITestCase

from .routers import APIRouters

# Test cases creating a django superuser account
SUPERUSER_TEST_ARGS = {
    'username': 'superuser',
    'email': 'superuser@example.com',
    'is_superuser': True,
    'password': 'foobar'
}


class BaseTestCase:
    """
    Common base class for test cases fo models and APIs
    """
    model = None
    serializer_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_factory = RequestFactory()

    def create_superuser(self):
        user = get_user_model().objects.create_user(**SUPERUSER_TEST_ARGS)
        self.assertTrue(user.is_superuser)
        return user, SUPERUSER_TEST_ARGS['password']

    def get_mock_request(self, method, path, **kwargs):
        user = kwargs.pop('user', None)

        if method not in ('get', 'post', 'put', 'patch', 'delete'):
            raise ValueError('Unsupported request factory method; {}'.format(method))

        request = getattr(self.request_factory, method)(path, **kwargs)
        request.user = user
        return request


@pytest.mark.model_tests
class ModelTestCase(BaseTestCase, DjangoTestCase):
    """
    Common unit test case for model specific django tests
    """
    model = None
    serializer_class = None

    def setUp(self):
        for attr in ('model', 'serializer_class'):
            if getattr(self, attr) is None:
                raise NotImplementedError('ModelTestCase requires instance variable {}'.format(attr))
        super().setUp()

    def create_valid_record(self, attrs):
        """
        Create record with serializer's create method validating data
        """
        serializer = self.serializer_class()
        validated_attrs = serializer.validate(attrs)
        self.assertIsInstance(
            validated_attrs,
            dict,
            'Serializer validate() did not return dictionary'
        )
        return serializer.create(validated_attrs)

    def assertInvalidRecordValidationError(self, attrs):
        """
        Try creating invalid record, must raise ValidationError
        """
        with self.assertRaises(ValidationError):
            self.serializer_class().validate(attrs)

    def assertPermissionDeniedValidationError(self, attrs):
        """
        Try creating invalid record, must raise ValidationError
        """
        with self.assertRaises(PermissionDenied):
            self.serializer_class().validate(attrs)


@pytest.mark.serializer_tests
class SerializerTestCase(BaseTestCase, DRFAPITestCase):
    """
    Common base test case for serializer specific django tests

    To use this class you need to define class variable serializer_class to the
    serializer class to test
    """
    model = None
    serializer_class = None

    def setUp(self):
        for attr in ('model', 'serializer_class'):
            if getattr(self, attr) is None:
                raise NotImplementedError('SerializerTestCase requires class variable {}'.format(attr))

    def validate_serializing_list_of_items_to_dict(self, instances, context=None):
        """
        Validate serializer serializes list of specified items to dict

        Normally instances is a queryset of models, but may be just a list for non-model
        serializers
        """

        if isinstance(instances, QuerySet):
            if instances.count() == 0:
                raise ValueError('Tested queryset is empty')
        elif isinstance(instances, list) or isinstance(instances, tuple):
            if len(instances) == 0:
                raise ValueError('No instances to test')
        else:
            raise TypeError('Instances must be instance of django.db.models.Queryset, list or tuple')

        for instance in instances:
            if context is not None:
                data = self.serializer_class(instance=instance, context=context).data
            else:
                data = self.serializer_class(instance=instance).data
            self.assertIsInstance(data, dict)


@pytest.mark.api_tests
class APITestCase(BaseTestCase, DRFAPITestCase):
    """
    Common base test case for DRF API tests
    """

    def setUp(self):
        self.routers = APIRouters()

    def get_url_from_view_arguments(self, view_name, query_args=None):
        """
        Parse URL from view name and optional arguments
        """
        url = reverse(view_name)
        if query_args:
            if not isinstance(query_args, str):
                query_args = urlencode(query_args, doseq=True)
            url = '{}?{}'.format(url, query_args)
        return url

    def get_login_arguments(self, user, password):
        """
        Get login arguments for user

        By default gets username field and users password, override as necessary
        """
        return {
            user._meta.model.USERNAME_FIELD: getattr(user, user._meta.model.USERNAME_FIELD),
            'password': password
        }

    def get_serializer_for_url_pattern(self, url_pattern, action='list'):
        """
        Return serializer for specified URL pattern
        """
        return url_pattern.item.callback.cls(action=action).get_serializer_class()

    def get_page_size(self, data):
        """
        Get page size for response
        """
        if isinstance(data, dict):
            page_size = data.get('page_size', None)
            if page_size is not None:
                return int(page_size)
            else:
                results = data.get('results', None)
                if results is not None:
                    return len(results)
                else:
                    raise NotImplementedError('Error detecting page size from response data')
        elif isinstance(data, list):
            return len(data)

    def get_expected_queryset(self, url_pattern, expected_item_count=None):
        """
        Return expected query set
        """
        if expected_item_count is not None:
            return url_pattern.queryset[:expected_item_count]
        else:
            return url_pattern.queryset

    def load_json_test_data(self, filename):
        """
        Load test JSON data with relative filename
        """

        try:
            return json.loads(open(filename, 'r').read())
        except Exception as e:
            raise OSError('Error loading {}: {}'.format(filename, e))

    def compare_record_to_data(self, record, data):
        """
        Compare fields returned in response to expected data
        """

        testserver_url_prefix = 'http://testserver'
        for key, value in data.items():
            if key not in record:
                raise ValidationError('Key {} not found in record {}'.format(key, record))

            if isinstance(record[key], str):
                # Hyperlinked fields have full link in record, relative link in data
                if record[key][:len(testserver_url_prefix)] == testserver_url_prefix:
                    record[key] = record[key][len(testserver_url_prefix):]

            if value == 'true':
                self.assertEqual(record[key], True, '{}=True {}'.format(key, record))
            elif value == 'false':
                self.assertEqual(record[key], False, '{}=False {}'.format(key, record))
            else:
                self.assertEqual(record[key], value, '{}={} {}'.format(key, value, record))

    def validate_option_list(self, data, expected_results_count=None):
        """
        Validate option list API response

        Option lists contain list/tuple of tuples with two arguments, used for
        filling option lists in forms
        """

        self.assertIsInstance(data, tuple)

        if expected_results_count is not None:
            self.assertEqual(len(data), expected_results_count)

        for option in data:
            self.assertIsInstance(option, tuple)
            self.assertEqual(len(option), 2)


    def validate_record(self, record, serializer, fields, allow_null_value=()):
        """
        Check some fields in response cloud record
        """

        for attr, expected_type in fields.items():
            self.assertTrue(
                attr in record.keys(),
                'Missing required attribute {}'.format(attr)
            )
            if record[attr] is None:
                if attr in allow_null_value:
                    continue
                raise AssertionError('Field {} returned unexpected None'.format(attr))
            self.assertIsInstance(
                record[attr],
                expected_type,
                'Unexpected type {} for field {} in {}'.format(
                    type(record[attr]),
                    attr,
                    record,
                )
            )

    def validate_result_set(self, view_name, response, queryset, serializer, fields,
                            allow_null_value=(), expected_result_count=None):
        """
        Validate result from list view
        """

        if expected_result_count is None:
            expected_result_count = queryset.count()

        if isinstance(response.data, dict):
            if 'results' in response.data:
                result_count = len(response.data['results'])
            else:
                raise ValueError('Unexpected django API response. You may need to override validate_result_set')
        elif isinstance(response.data, list):
            result_count = len(response.data)
        else:
            raise ValueError('Unexpected response data type. You may need to override validate_result_set')

        self.assertEqual(
            result_count,
            expected_result_count,
            'Expected total {} {} results, received {}'.format(
                expected_result_count,
                view_name,
                result_count,
            )
        )

        if fields:
            for record in response.data['results']:
                self.validate_record(record, serializer, fields, allow_null_value)

    def validate_login_required_redirection(self, url, expected_redirect):
        """
        Validate specified URL without authentication goes to login page with correct
        page in next query argument
        """

        # Get index URL without following redirects
        res = self.client.get(url, allow_redirection=False)

        # Ensure we get redirection to login page without logging in
        self.assertIsInstance(
            res,
            HttpResponseRedirect,
            'Did not receive a HttpResponseRedirect object'
            )
        self.assertEqual(
            res.status_code,
            status.HTTP_302_FOUND,
            'No 302 redirection detected'
        )

        # Ensure redirect points to correct login page
        redirect = res.get('Location', None)
        self.assertIsInstance(
            redirect,
            str,
            'Redirection header not found'
        )
        self.assertEqual(
            redirect,
            expected_redirect,
            'Received unexpected login redirect {}'.format(redirect)
        )

    def validate_public_page_load(self, url, user, password,
                                  expected_success_code=status.HTTP_200_OK):
        """
        Login with given credentials and ensure page return HTTP 200
        """

        self.client.logout()

        # Load page without authentication
        res = self.client.get(url)
        self.assertEqual(res.status_code, expected_success_code)

        # Load page as authenticated user
        self.client.login(**self.get_login_arguments(user, password))
        res = self.client.get(url)
        self.assertEqual(res.status_code, expected_success_code)

        return res

    def validate_protected_page_load(self, url, user, password, expected_redirect,
                                     expected_success_code=status.HTTP_200_OK):
        """
        Validate protected page with login redirection goes to excepted redirect page
        - Login with given credentials and ensure page return HTTP 200 and unauthencicated
        """

        res = self.client.get(url)

        self.client.logout()
        self.validate_login_required_redirection(url, expected_redirect)

        self.client.login(**self.get_login_arguments(user, password))
        res = self.client.get(url)
        self.assertEqual(res.status_code, expected_success_code)

        return res

    def validate_public_api_listing(self, view_name, query_args=None,
                                    fields=None, allow_null_value=(),
                                    expected_success_code=status.HTTP_200_OK,
                                    expected_results_count=None):
        """
        Validate listing from public API

        Public API is visible without authentication and as logged in user
        """

        url_pattern = self.routers.get_view_url_pattern(view_name)
        serializer = self.get_serializer_for_url_pattern(url_pattern, action='list')
        url = self.get_url_from_view_arguments(view_name, query_args)
        self.client.logout()

        # Login and get page without login
        res = self.client.get(url)
        self.assertEqual(res.status_code, expected_success_code)

        # Get expected queryset and validate result set
        if expected_success_code == status.HTTP_200_OK:
            queryset = self.get_expected_queryset(url_pattern, self.get_page_size(res.data))
            self.validate_result_set(
                view_name,
                res,
                queryset,
                serializer,
                fields,
                allow_null_value,
                expected_results_count,
            )
        return res, url_pattern, serializer

    def validate_protected_api_listing(self, user, password, view_name,
                                       query_args=None, fields=None, allow_null_value=(),
                                       expected_failure_code=status.HTTP_401_UNAUTHORIZED,
                                       expected_success_code=status.HTTP_200_OK,
                                       expected_results_count=None):
        """
        Validate listing from API requiring authentication

        Protected API returns failure (by default 401 Forbidden) for unauthenticated
        users and is shown normally to authenticated user
        """

        url_pattern = self.routers.get_view_url_pattern(view_name)
        serializer = self.get_serializer_for_url_pattern(url_pattern, action='list')
        url = self.get_url_from_view_arguments(view_name, query_args)
        self.client.logout()

        # Get URL as unauthenticated user, verify failure code
        res = self.client.get(url)
        self.assertEqual(res.status_code, expected_failure_code)

        # Login and get page as user, check expected status code
        self.client.login(**self.get_login_arguments(user, password))
        res = self.client.get(url)
        self.assertEqual(res.status_code, expected_success_code)

        # Get expected queryset and validate result set
        if expected_success_code == status.HTTP_200_OK:
            queryset = self.get_expected_queryset(url_pattern, self.get_page_size(res.data))
            self.validate_result_set(
                view_name,
                res,
                queryset,
                serializer,
                fields,
                allow_null_value,
                expected_results_count,
            )

        return res, url_pattern, serializer

    def create_record(self, user, password, view_name, data):
        """
        Create a new record with POST to API and validate results
        """

        url = reverse(view_name)

        self.client.logout()
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(**self.get_login_arguments(user, password))
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)

        record = json.loads(res.content)
        self.compare_record_to_data(record, data)

        return record

    def update_record(self, user, password, view_name, record_id, data):
        """
        Update a new record with POST to API and validate results
        """

        url = '{}/{}'.format(reverse(view_name), record_id)

        self.client.logout()
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(**self.get_login_arguments(user, password))
        res = self.client.put(url, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)

        record = json.loads(res.content)
        self.compare_record_to_data(record, data)

        return record

    def delete_record(self, user, password, view_name, record_id):
        """
        Delete record from database
        """

        url = '{}/{}'.format(reverse(view_name), record_id)

        self.client.logout()
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(**self.get_login_arguments(user, password))
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


    def get_record(self, user, password, view_name, record_id):
        """
        Get detail record with record_id
        """

        url = '{}/{}'.format(reverse(view_name), record_id)

        self.client.logout()
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(**self.get_login_arguments(user, password))
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        record = json.loads(res.content)
        return record

    def validate_missing_record_not_found(self, user, password, view_name, record_id):
        """
        Validate getting a record with invalid ID, raising HTTP 404
        """

        url = '{}/{}'.format(reverse(view_name), record_id)

        self.client.logout()
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(**self.get_login_arguments(user, password))
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        return res

    def validate_get_page_permission_denied(self, user, password, view_name):
        """
        Validate we get permission denied message when trying to get a page
        """

        url = reverse(view_name)
        self.client.logout()
        self.client.login(**self.get_login_arguments(user, password))
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)
        return res

    def validate_create_record_permission_denied(self, user, password, view_name, data):
        """
        Validate we get permission denied message when trying to create record as
        unauthorized user
        """

        url = reverse(view_name)

        self.client.logout()
        self.client.login(**self.get_login_arguments(user, password))
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)
        return res

    def validate_update_record_permission_denied(self, user, password, view_name, record_id, data):
        """
        Validate we get permission denied message when trying to create record as
        unauthorized user
        """

        url = '{}/{}'.format(reverse(view_name), record_id)

        self.client.logout()
        self.client.login(**self.get_login_arguments(user, password))
        res = self.client.put(url, data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)
        return res

    def validate_delete_permission_denied(self, user, password, view_name, record_id):
        """
        Validate we get permission denied message when trying to create record as
        unauthorized user
        """
        url = '{}/{}'.format(reverse(view_name), record_id)

        self.client.logout()
        self.client.login(**self.get_login_arguments(user, password))
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)
        return res
