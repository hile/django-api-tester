
from rest_framework.serializers import ValidationError


class BaseValidator:
    """
    Common base validator class

    Implements a validator to use with serializers that calls configured child
    class validator methods in order.

    To use this class:
    - inherit in child class, defining validator methods starting with validate_
    - if order of validators is important, name the classes in self.validators in order

    Use in a serializer to validate like:

       def validate(self, attrs):
           return MyValidator(attrs).validate()

    Note: always raise rest_framework.serializers.ValidationError for validation errors.
    """

    def __init__(self, attrs):
        self.attrs = attrs

    def __call__(self):
        """
        Call self.validate(). Compatibility for early code
        """

    def get_validators(self):
        """
        Return names of validator methods for class

        Returns primarily class variable 'validators', or any methods of class starting
        with name validate_.

        Note: setting explicit 'validators' class variable allows setting ordering. The
        automatic detection returns list of sorted callback names
        """
        validator_names = getattr(self, 'validators', None)
        if validator_names:
            return validator_names
        else:
            return sorted(key for key in dir(self) if key[:9] == 'validate_' and callable(getattr(self, key)))

    def validate(self):
        """
        Call validator method names specified by self.get_validators()
        """

        validator_method_names = self.get_validators()
        if not validator_method_names:
            raise ValidationError('Validator defines no validators')

        for name in validator_method_names:
            callback = getattr(self, name)
            if not callable(callback):
                raise ValidationError('Not a callable method of {}: {}'.format(self.__class__, name))
            callback()

        return self.attrs
