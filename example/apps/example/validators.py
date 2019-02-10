
from django_api_tester.validator import BaseValidator, ValidationError


class ExampleValidatior(BaseValidator):
    """
    Example model validator
    """
    validators = (
        'validate_required_fields',
        'validate_label',
    )

    def validate_required_fields(self):
        """
        Example callback for validating formatting of required fields.

        This is normally done by serializer anyway, but just shows how multiple
        validators are configured.
        """
        label = self.attrs.get('label', None)
        if not label:
            raise ValidationError('No label specified')

    def validate_label(self):
        """
        Validate label attribute format

        Just as an example, require valid label to start with word 'test'
        """
        try:
            label = self.attrs.get('label', None)
            fields = label.split()
            if fields[0] != 'test':
                raise ValidationError('Label must start with word test')
        except Exception:
            raise ValidationError('Error parsing label')


class ExampleUUIDValidatior(BaseValidator):
    """
    Example UUID validator

    Example how validators are autoloaded alphabetically. Not recommended, order of
    validator calls can be confusing when this is done!
    """

    def validate_then(self):
        """
        Second validator when no validators class variable is given
        """
        label = self.attrs.get('label', None)
        if not label:
            raise ValidationError('Still no label specified')

    def validate_first(self):
        """
        First validator when no validators class variable is given
        """
        label = self.attrs.get('label', None)
        if not label:
            raise ValidationError('No label specified')
