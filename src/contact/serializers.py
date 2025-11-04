from rest_framework import serializers
from .models import Contact, StateRecord


class ContactSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    organization_uuid = serializers.ReadOnlyField()

    class Meta:
        model = Contact
        exclude = ('user_uuid',)

    def validate_type(self, value):
        if not value:
            raise serializers.ValidationError(
                "type must be an array of one or more string elements"
            )
        return value


class ContactNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('contact_uuid', 'first_name', 'middle_name', 'last_name')


class ContactIndexSerializer(serializers.ModelSerializer):
    """
    Serializer for saving to ElasticSearchIndex.
    """
    organization_uuid = serializers.ReadOnlyField()

    class Meta:
        model = Contact
        fields = '__all__'


class StateRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for StateRecord model.
    """

    class Meta:
        model = StateRecord
        fields = '__all__'
