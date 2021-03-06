"""
Utility functions for iterating DRF APIs
"""

import re

from django.conf import settings
from django.urls import URLResolver
from rest_framework import viewsets, views

IGNORE_ROUTER_NAMES = (None, 'admin', 'rest_framework')
IGNORE_FORMAT = r'.(?P<format>[a-z0-9]+)/?'


class Router:
    """
    Custom class to represent API router for testing purposes

    Links API views and view sets to self.url_patterns
    """

    def __init__(self, router):
        self.router = router
        self.url_patterns = []
        for item in self.router.url_patterns:
            if hasattr(item.callback, 'cls') and isinstance(item.callback.cls(), views.View):
                self.url_patterns.append(RouterURLPattern(self, item))
            if hasattr(item.callback, 'cls') and isinstance(item.callback.cls(), viewsets.GenericViewSet):
                self.url_patterns.append(RouterURLPattern(self, item))

    def __repr__(self):
        return self.prefix

    def __eq__(self, other):
        if self.router.namespace != other.router.namespace:
            return self.router.namespace == other.router.namespace
        if hasattr(self.router, 'app_name') and hasattr(other.router, 'app_name'):
            return self.router.app_name == other.router.namespace
        return 0

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if self.router.namespace != other.router.namespace:
            return self.router.namespace < other.router.namespace
        if hasattr(self.router, 'app_name') and hasattr(other.router, 'app_name'):
            return self.router.app_name < other.router.namespace
        return 0

    def __gt__(self, other):
        if self.router.namespace != other.router.namespace:
            return self.router.namespace > other.router.namespace
        if hasattr(self.router, 'app_name') and hasattr(other.router, 'app_name'):
            return self.router.app_name > other.router.namespace
        return 0

    def __le__(self, other):
        if self.router.namespace != other.router.namespace:
            return self.router.namespace <= other.router.namespace
        if hasattr(self.router, 'app_name') and hasattr(other.router, 'app_name'):
            return self.router.app_name <= other.router.namespace
        return 0

    def __ge__(self, other):
        if self.router.namespace != other.router.namespace:
            return self.router.namespace >= other.router.namespace
        if hasattr(self.router, 'app_name') and hasattr(other.router, 'app_name'):
            return self.router.app_name >= other.router.namespace
        return 0

    @property
    def prefix(self):
        """
        Return URL prefox for router
        """
        value = self.router.pattern.regex.pattern
        if value.startswith('^'):
            value = value[1:]
        return value

    def get_url_pattern(self, url_pattern):
        """
        Get URL pattern by string presentation
        """
        for item in self.url_patterns:
            if item.url_pattern == url_pattern:
                return item
        return None


class RouterURLPattern:
    """
    Wrap URL pattern from router to object with more properties
    """

    def __init__(self, router, item):
        self.router = router
        self.item = item

    def __repr__(self):
        return self.url_pattern

    @property
    def module(self):
        """
        Return model for pattern's callback
        """
        return self.item.callback.__module__

    @property
    def view(self):
        """
        Return view name for pattern's callback
        """
        return self.item.callback.__name__

    @property
    def url_pattern(self):
        """
        Return full URL pattern with router prefix
        """
        return '^{}{}'.format(self.router.prefix, self.suffix)

    @property
    def suffix(self):
        """
        Return URL pattern suffix
        """
        value = self.item.pattern.regex.pattern
        if value.startswith('^'):
            value = value[1:]
        return value

    @property
    def query_arg_groups(self):
        """
        Return query argument groups parsed from regex patterns
        """
        return re.compile(r'\(\?P<([^>]+)>').findall(self.item.pattern.regex.pattern)

    @property
    def queryset(self):
        """
        Return queryset used with router, or empty list if not defined
        """
        cls = self.item.callback.cls
        if callable(getattr(cls(), 'get_queryset', None)):
            return self.item.callback.cls().get_queryset()
        elif getattr(cls, 'queryset', None) is not None:
            return self.item.callback.cls.queryset

        raise NotImplementedError('View {} does not implement queryset or get_queryset'.format(cls))

    @property
    def view_name(self):
        """
        Return formatted full name of view with namespace
        """
        return '{}{}'.format(
            '{}:'.format(self.router.router.namespace) if self.router.router.namespace else '',
            self.item.name,
        )


class APIRouters(list):
    """
    All relevant API routes

    Note: this may skip some routes. Code has been mainly tested with class based model views.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for router in __import__(settings.ROOT_URLCONF).urls.urlpatterns:
            if not isinstance(router, URLResolver):
                continue
            if router.app_name in IGNORE_ROUTER_NAMES:
                continue
            self.append(Router(router))

        self.sort()

    def get_router_for_namespace(self, namespace):
        """
        Get router for given namespace
        """
        for router in self:
            if router.router.namespace == namespace:
                return router
        return None

    def get_view_url_pattern(self, view_name):
        """
        Find url pattern for named view
        """
        for router in self:
            for url_pattern in router.url_patterns:
                if url_pattern.view_name == view_name:
                    return url_pattern
        raise ValueError('No such view: {}'.format(view_name))
