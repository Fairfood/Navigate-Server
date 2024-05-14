from rest_framework import serializers
from datetime import datetime
from pytz import timezone
from rest_framework.exceptions import ValidationError
from django.conf import settings
from django.db import models


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
    


