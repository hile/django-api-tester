
Django model and rest framework test utilities
==============================================

This module contains utilities to help in writing unit tests for django
models and django rest framework API endpoints.

The module has been tested with namespaced django apps. It also requires many
additional coding style conventions to do anything useful:

- it's recommended to namespace all django apps. To support namespace detection
  in django_api_tester.routers.APIRouters you should have app_name in apps' urls.py
- serializer's validate() method should call a validator class that inherits
  django_api_tester.validator.BaseValidator

Installing and configuring
==========================

This package should be installed to your django environment.

For example:

pip install django-api-tester

There is normally no need to add the application to django apps.

Usage
=====

Django API tester extends following test cases classes:

- django.test.TestCase used for django model tests
- rest_framework.test.APITestCase for DRF API tests

Examples
--------

Example application using these modules is in directory example/.
