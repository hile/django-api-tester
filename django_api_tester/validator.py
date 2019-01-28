
from rest_framework.serializers import ValidationError


class BaseValidator:
    """
    Common base validator class

    Implements a validator to use with serializers that calls configured
    child class validator methods in order.
    """

    # Validator methods in self to call in order
    validators = ()

    def __init__(self, attrs):
        self.attrs = attrs

    def __call__(self):
        """
        Call validator methods specified in self.validators
        """

        if not self.validators:
            raise ValidationError('Validator defines no validators')

        for name in self.validators:
            getattr(self, name)()

        return self.attrs
