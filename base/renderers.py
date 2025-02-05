"""Custom render class to custom success response."""
from hashid_field import Hashid
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.encoders import JSONEncoder


class HashIDJSONEncoder(JSONEncoder):
    """A JSONEncoder subclass that can encode objects of the Hashid class.

    When an object of the Hashid class is encountered during encoding, it is
    converted to a string representation of the hashid value.

    All other objects are encoded using the superclass's default encoding
    method.

    Example usage:
    ```
    import json
    from hashid_field import Hashid
    from my_module import HashidJSONEncoder

    data = {
        'id': Hashid(123),
        'name': 'Alice'
    }

    json_str = json.dumps(data, cls=HashidJSONEncoder)
    ```

    In the example above, the Hashid object with value 123 will be converted
    to a JSON string during encoding, while the 'name' field will be encoded
    using the default encoding method of the JSONEncoder superclass.
    """

    def default(self, o):
        """Override the default method of JSONEncoder to support encoding of
        Hashid objects.

        Args:
            o (Any): The object to encode.

        Returns:
            Any: The encoded value.
        """
        if isinstance(o, Hashid):
            return str(o)
        return super().default(o)


class HashIDRenderer(JSONRenderer):
    """
    A custom renderer that serializes data using JSON format and encodes
    sensitive information using HashID encoding.
    """

    encoder_class = HashIDJSONEncoder

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Custom render function."""
        response_data = data
        try:
            if not data["success"]:
                response_data = data
        except Exception:
            response_data = {
                "success": True,
                "errors": [],
                "code": renderer_context["response"].status_code,
                "data": data,
            }
        try:
            getattr(
                renderer_context.get("view").get_serializer().Meta,
                "resource_name",
                "objects",
            )
        except Exception:
            pass

        response = super().render(
            response_data, accepted_media_type, renderer_context
        )

        return response
