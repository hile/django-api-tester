
from rest_framework import routers

from .views import ExampleViewSet, ExampleUUIDViewSet


class APIRootView(routers.APIRootView):
    """
    Root view for example API.
    """


class APIRouter(routers.DefaultRouter):
    APIRootView = APIRootView

    def get_lookup_regex(self, viewset, lookup_prefix=''):
        if viewset == ExampleUUIDViewSet:
            return r'(?P<uuid>[^/.]+)'
        return r'(?P<pk>[^/.]+)'


router = APIRouter(trailing_slash=False)
router.register('simple-examples', ExampleViewSet, basename='example')
router.register('uuid-examples', ExampleUUIDViewSet, basename='example-uuid')

app_name = 'example'
urlpatterns = router.urls
