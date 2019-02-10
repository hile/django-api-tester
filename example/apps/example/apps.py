
import os

from django.apps import AppConfig

APP_DESCRIPTION_DOCSTRING = """
Example django application.
"""


class ExampleAppConfig(AppConfig):
    path = os.path.dirname(__file__)
    name = 'apps.example'
    verbose_name = APP_DESCRIPTION_DOCSTRING

    def ready(self):
        """
        Import signals after app is ready
        """
        #from .signals.member import create_auth_token  # noqa
