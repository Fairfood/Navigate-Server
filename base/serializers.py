from rest_framework import serializers

class IDModelSerializer(serializers.ModelSerializer):
    """
    Serializer class for models with an 'id' field.
    """
    id = serializers.CharField(read_only=True)