from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

from . import model_factories as mfactories
from ..serializers import ContactSerializer, ContactNameSerializer


class ContactSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_contains_expected_fields(self):
        contact = mfactories.Contact()

        request = self.factory.get('/')

        serializer_context = {
            'request': Request(request),
        }

        serializer = ContactSerializer(instance=contact,
                                       context=serializer_context)

        data = serializer.data

        keys = [
            'contact_uuid',
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'addresses',
            'title',
            'url',
            'phones',
            'company',
            'contact_type',
            'customer_type',
            'notes',
            'emails'
        ]

        self.assertEqual(set(data.keys()), set(keys))


class ContactNameSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_contains_expected_fields(self):
        contact = mfactories.Contact()

        serializer = ContactNameSerializer(instance=contact)

        data = serializer.data

        keys = [
            'contact_uuid',
            'first_name',
            'middle_name',
            'last_name'
        ]

        self.assertEqual(set(data.keys()), set(keys))
