from datetime import datetime

from django.conf import settings
from hashid_field.field import Hashid
from pytz import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


def unix_to_datetime(unix_time):
    """Function to convert Unix timestamps to date time."""
    try:
        unix_time = float(unix_time)
        localtz = timezone(settings.TIME_ZONE)
        date = localtz.localize(datetime.fromtimestamp(unix_time))
        return date
    except ValueError:
        raise ValidationError("Unix timestamps must be float or int")


class UnixDateTimeField(serializers.DateTimeField):
    """A custom field to accept Unix timestamps in a DateTimeField.

    This field extends `serializers.DateTimeField` to enable the use of Unix
    timestamps, which are represented as integers representing the number of
    seconds since the Unix epoch (January 1, 1970, 00:00:00 UTC).

    Usage:
        If you want to include this field in a serializer, you should add it as
        a class attribute, like this:
        ```
        class MySerializer(serializers.ModelSerializer):
            unix_datetime = UnixDateTimeField()
            ...
        ```
    """

    def to_internal_value(self, data):
        """Converts a Unix timestamp to a Python datetime object.

        Args:
            data (int): The Unix timestamp to convert.

        Returns:
            datetime: The corresponding Python datetime object.
        """
        # delegate conversion to a separate function
        return unix_to_datetime(data)

class SerializableRelatedField(serializers.PrimaryKeyRelatedField):
    """A custom related field that can serialize related objects using a
    specified serializer."""

    def __init__(self, serializer=None, **kwargs):
        """Initializes the field with a specified serializer.

        Args:
            serializer: The serializer to use for serializing related objects.
            kwargs: Additional keyword arguments to pass to the base class.
        """
        self.serializer = serializer
        self.many = kwargs.get("many", False)
        super().__init__(**kwargs)

    def use_pk_only_optimization(self):
        """Disable the primary key optimization.

        By default, this field uses primary key optimization, which may not be
        suitable for custom serialization. So, we disable it here.

        Returns:
            False to disable primary key optimization.
        """
        return False

    def single_to_representation(self, value):
        """Convert a single related object to its serialized representation.

        Args:
            value: The related object to serialize.

        Returns:
            The serialized representation of the related object.
        """

        if not value:
            return None
        if isinstance(value, Hashid):
            return value
        return value.pk

    def to_representation(self, value):
        """Serializes the related object using the specified serializer.

        If no serializer is specified, delegates to the base class
        implementation.

        Args:
            value: The related object to serialize.

        Returns:
            The serialized representation of the related object.
        """
        if self.serializer is not None:
            return self.serializer(value, many=self.many).data
        if self.many:
            return [self.single_to_representation(obj) for obj in value]
        return self.single_to_representation(value)


