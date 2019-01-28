
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.test import TestCase as DjangoTestCase
from django.urls import reverse
from rest_framework import status
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

    def create_superuser(self):
        user = get_user_model().objects.create_user(**SUPERUSER_TEST_ARGS)
        self.assertTrue(user.is_superuser)
        return user, SUPERUSER_TEST_ARGS['password']


class ModelTestCase(BaseTestCase, DjangoTestCase):
    """
    Common base model unit test case for tukkimies
    """

    def setUp(self):
        super().setUp()

    def create_valid_record(self, attrs):
        """
        Create record after validating data
        """
        validated_attrs = self.serializer_class().validate(attrs)
        self.assertIsInstance(
            validated_attrs,
            dict,
            'Serializer validate() did not return dictionary'
        )
        return self.model.objects.create(**validated_attrs)

    def assertInvalidRecordValidationError(self, attrs):
        """
        Try creating invalid record, must raise ValidationError
        """
        with self.assertRaises(ValidationError):
            self.serializer_class().validate(attrs)


class APITestCase(BaseTestCase, DRFAPITestCase):
    """
    Common base API test case for tukkimies
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

    def get_expected_queryset(self, url_pattern, expected_item_count=None):
        """
        Return expected query set
        """
        if expected_item_count is not None:
            return url_pattern.queryset[:expected_item_count]
        else:
            return url_pattern.queryset

    def validate_option_list(self, data):
        """
        Validate option list API response

        Option lists contain list/tuple of tuples with two arguments, used for
        filling option lists in forms
        """

        self.assertIsInstance(data, tuple)
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

        self.assertEqual(
            len(response.data['results']),
            expected_result_count,
            'Expected total {} {} results, received {}'.format(
                expected_result_count,
                view_name,
                len(response.data['results']),
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
            queryset = self.get_expected_queryset(url_pattern, res.data['page_size'])
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

        print('get_login_arguments', user, password, self.get_login_arguments(user, password))
        # Login and get page as user, check expected status code
        self.client.login(**self.get_login_arguments(user, password))
        res = self.client.get(url)
        self.assertEqual(res.status_code, expected_success_code)

        # Get expected queryset and validate result set
        if expected_success_code == status.HTTP_200_OK:
            queryset = self.get_expected_queryset(url_pattern, res.data['page_size'])
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
