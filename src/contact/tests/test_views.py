import json
import uuid

from django.test import TestCase

from rest_framework.test import APIRequestFactory

from . import model_factories as mfactories
from ..models import Contact, EMAIL_TYPE_CHOICES, PHONE_TYPE_CHOICES
from ..views import ContactViewSet


class ContactListViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = mfactories.User()
        self.organization_uuid = str(uuid.uuid4())
        self.wflvl1 = str(uuid.uuid4())
        self.wflvl2 = str(uuid.uuid4())
        self.session = {
            'jwt_organization_uuid': self.organization_uuid,
            'jwt_username': 'Test User',
            'jwt_user_uuid': uuid.uuid4()
        }

    def test_list_empty(self):
        request = self.factory.get('')
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_list_contacts(self):
        mfactories.Contact(
            first_name='David',
            addresses=[
                {
                    'type': 'billing',
                    'street': 'Bówie St',
                    'house_number': '22',
                    'postal_code': '78703',
                    'city': 'Austin',
                    'country': 'United States',
                },
            ],
            emails=[
                {'type': 'private', 'email': 'contact@bowie.co.uk'},
                {'type': 'office', 'email': 'bowie@label.co.uk'},
            ],
            notes="Bowie's notes"
        )

        request = self.factory.get('')
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        contact = response.data[0]
        self.assertTrue('id' in contact)
        self.assertEqual(contact['first_name'], 'David')
        self.assertEqual(
            contact['addresses'],
            [
                {
                    'type': 'billing',
                    'street': 'Bówie St',
                    'house_number': '22',
                    'postal_code': '78703',
                    'city': 'Austin',
                    'country': 'United States',
                },
            ])
        self.assertEqual(
            contact['emails'],
            [
                {'type': 'private', 'email': 'contact@bowie.co.uk'},
                {'type': 'office', 'email': 'bowie@label.co.uk'},
            ])
        self.assertEqual(contact['notes'], "Bowie's notes")

    def test_list_contacts_diff_user_same_org(self):
        mfactories.Contact(
            first_name='David',
            addresses=[
                {
                    'type': 'billing',
                    'street': 'Bówie St',
                    'house_number': '22',
                    'postal_code': '78703',
                    'city': 'Austin',
                    'country': 'United States',
                },
            ],
            emails=[
                {'type': 'private', 'email': 'contact@bowie.co.uk'},
                {'type': 'office', 'email': 'bowie@label.co.uk'},
            ],
            notes="Bowie's notes"
        )
        request = self.factory.get('')
        user_other = mfactories.User(first_name='John', last_name='Lennon')
        request.user = user_other
        request.session = self.session
        view = ContactViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_contacts_diff_org(self):
        mfactories.Contact(
            first_name='David',
            addresses=[
                {
                    'type': 'billing',
                    'street': 'Bówie St',
                    'house_number': '22',
                    'postal_code': '78703',
                    'city': 'Austin',
                    'country': 'United States',
                },
            ],
            emails=[
                {'type': 'private', 'email': 'contact@bowie.co.uk'},
                {'type': 'office', 'email': 'bowie@label.co.uk'},
            ],
            notes="Bowie's notes"
        )
        request = self.factory.get('')
        user_other = mfactories.User(first_name='John', last_name='Lennon')
        request.user = user_other
        request.session = self.session
        request.session["jwt_organization_uuid"] = str(uuid.uuid4())
        view = ContactViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_contacts_ordering_asc(self):
        mfactories.Contact.create_batch(size=2)

        request = self.factory.get('', {'ordering': 'first_name'})
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['first_name'], 'David')
        self.assertEqual(response.data[1]['first_name'], 'Nina')

    def test_list_contacts_ordering_desc(self):
        mfactories.Contact.create_batch(size=2)

        request = self.factory.get('', {'ordering': '-first_name'})
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['first_name'], 'Nina')
        self.assertEqual(response.data[1]['first_name'], 'David')

    def test_list_contacts_anonymoususer(self):
        request_get = self.factory.get('')
        view = ContactViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 403)


class ContactRetrieveViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = mfactories.User()
        self.organization_uuid = str(uuid.uuid4())
        self.session = {
            'jwt_organization_uuid': self.organization_uuid,
            'jwt_username': 'Test User',
            'jwt_user_uuid': uuid.uuid4()
        }

    def test_retrieve_contact(self):
        contact = mfactories.Contact(user_uuid=self.session['jwt_user_uuid'])
        request = self.factory.get('')
        request.user = self.user
        request.session = self.session

        view = ContactViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=contact.pk)

        self.assertEqual(response.status_code, 200)

    def test_retrieve_contact_superuser(self):
        contact = mfactories.Contact(user_uuid=uuid.uuid4())
        request = self.factory.get('')
        su = mfactories.User()
        su.is_superuser = True
        su.save()

        request.user = su
        request.session = self.session

        view = ContactViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=contact.pk)

        self.assertEqual(response.status_code, 200)

    def test_retrieve_contact_diff_org(self):
        contact = mfactories.Contact(user_uuid=uuid.uuid4())
        request = self.factory.get('')
        request.user = self.user
        request.session = self.session
        request.session["jwt_organization_uuid"] = str(uuid.uuid4())
        view = ContactViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=contact.pk)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_contact_not_owner(self):
        contact = mfactories.Contact(user_uuid=uuid.uuid4())

        request = self.factory.get('')
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=contact.pk)
        self.assertEqual(response.status_code, 200)

    def test_list_contacts_anonymoususer(self):
        request_get = self.factory.get('')
        view = ContactViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 403)


class ContactCreateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = mfactories.User()
        self.organization_uuid = str(uuid.uuid4())
        self.wflvl1 = str(uuid.uuid4())
        self.wflvl2 = str(uuid.uuid4())
        self.session = {
            'jwt_organization_uuid': self.organization_uuid,
            'jwt_username': 'Test User',
            'jwt_user_uuid': uuid.uuid4()
        }

    def test_create_contact_minimal(self):
        data = {
            'first_name': 'Máx',
            'last_name': 'Cöoper'
        }

        request = self.factory.post(  # trick to pass a list in a payload
            '', json.dumps(data), content_type='application/json')
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)

        contact = Contact.objects.get(pk=response.data['id'])
        self.assertEqual(contact.user_uuid, self.session['jwt_user_uuid'])
        self.assertEqual(contact.first_name, data['first_name'])
        self.assertEqual(contact.last_name, data['last_name'])

    def test_create_contact_org_and_user_set_by_jwt(self):
        data = {
            'first_name': 'Máx',
            'last_name': 'Cöoper',
            'user_uuid': 'Test',
        }

        request = self.factory.post(  # trick to pass a list in a payload
            '', json.dumps(data), content_type='application/json')
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)

        contact = Contact.objects.get(pk=response.data['id'])
        self.assertEqual(contact.user_uuid, self.session['jwt_user_uuid'])
        self.assertEqual(contact.first_name, data['first_name'])
        self.assertEqual(contact.last_name, data['last_name'])

    def test_create_contact_member_all_wflvl1s(self):
        data = {
            'first_name': 'Máx',
            'last_name': 'Cöoper'
        }

        request = self.factory.post(  # trick to pass a list in a payload
            '', json.dumps(data), content_type='application/json')
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'post': 'create'})

        response = view(request)
        self.assertEqual(response.status_code, 201)

    def test_create_contact_member_all_wflvl1s_unordered_and_extra(self):
        wflvl1_other = str(uuid.uuid4())
        wflvl1_extra = str(uuid.uuid4())

        data = {
            'first_name': 'Máx',
            'last_name': 'Cöoper'
        }

        request = self.factory.post(  # trick to pass a list in a payload
            '', json.dumps(data), content_type='application/json')
        request.user = self.user
        request.session = self.session

        view = ContactViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)

    def test_create_contact(self):
        data = {
            'first_name': 'Julio',
            'middle_name': 'José',
            'last_name': 'Iglesias',
            'title': 'mr',
            'contact_type': 'personnel',
            'customer_type': 'customer',
            'company': 'Columbia',
            'addresses': [
                {
                    'type': 'home',
                    'street': 'Francisco de Sales',
                    'house_number': '288',
                    'postal_code': '28003',
                    'city': 'Madrid',
                    'country': 'Spain',
                },
            ],
            'emails': [],
            'phones': [{'type': 'office', 'number': '123'}],
            'notes': 'I am the Spanish Gigolò',
        }

        request = self.factory.post(  # trick to pass structures in a payload
            '', json.dumps(data), content_type='application/json')
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'post': 'create'})

        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {**data, **response.data})

        contact = Contact.objects.get(pk=response.data['id'])
        self.assertEqual(contact.__dict__, {**contact.__dict__,  **data})

    def test_create_with_invalid_email(self):
        data = {
            'first_name': u'Máx',
            'last_name': u'Cöoper',
            'emails': [{'type': EMAIL_TYPE_CHOICES[0], 'email': 'bad'}]
        }
        request = self.factory.post(  # trick to pass a list in a payload
            '', json.dumps(data), content_type='application/json')
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            str(response.data['emails'][0]), 'Enter a valid email address.')
        self.assertEqual(response.data['emails'][0].code, 'invalid')

    def test_create_with_invalid_phone(self):
        data = {
            'first_name': u'Máx',
            'last_name': u'Cöoper',
            'phones': [{'type': PHONE_TYPE_CHOICES[0], 'number': '01'}]
        }
        request = self.factory.post(  # trick to pass a list in a payload
            '', json.dumps(data), content_type='application/json')
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            ("Invalid value: {'type': 'office', 'number': '01'}. List of "
             "'phone' objects with the structure:"),
            str(response.data['phones'][0]),
        )
        self.assertEqual(response.data['phones'][0].code, 'invalid')

    def test_create_with_invalid_address(self):
        data = {
            'first_name': u'Máx',
            'last_name': u'Cöoper',
            'addresses': [
                {
                    'type': 'FAKE',
                    'street': 'Oderberger Straße',
                    'house_number': '16A',
                    'postal_code': '10435',
                    'city': 'Berlin',
                    'country': 'Germany',
                },
            ]
        }
        request = self.factory.post(  # trick to pass a list in a payload
            '', json.dumps(data), content_type='application/json')
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "List of 'address' objects with the structure:",
            str(response.data['addresses'][0]),
        )
        self.assertEqual(response.data['addresses'][0].code, 'invalid')

    def test_create_contacts_anonymoususer(self):
        request = self.factory.post('', {})
        view = ContactViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 403)


class ContactUpdateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = mfactories.User()
        self.organization_uuid = str(uuid.uuid4())
        self.session = {
            'jwt_organization_uuid': self.organization_uuid,
            'jwt_username': 'Test User',
            'jwt_user_uuid': uuid.uuid4()
        }

    def test_update_contact_minimal(self):
        contact = mfactories.Contact()
        data = {
            'first_name': 'David',
            'middle_name': 'Keith',
            'last_name': 'Lynch',
        }
        request = self.factory.post('', data)
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'post': 'update'})

        response = view(request, pk=contact.pk)
        self.assertEqual(response.status_code, 200)

    def test_update_contact(self):
        contact = mfactories.Contact(emails=[{'type': 'private', 'email': 'emil@io.io'}])

        data = {
            'first_name': 'David',
            'middle_name': 'Keith',
            'last_name': 'Lynch',
            'addresses': [
                {
                    'type': 'home',
                    'street': 'Francisco de Sales',
                    'house_number': '288',
                    'postal_code': '28003',
                    'city': 'Madrid',
                    'country': 'Spain',
                },
            ],
            'emails': [],
            'phones': [
                {
                    'type': 'office',
                    'number': '12345',
                },
                {
                    'type': 'mobile',
                    'number': '67890',
                },
            ],
            'notes': 'My notes'
        }
        request = self.factory.post('', json.dumps(data),
                                    content_type='application/json')
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'post': 'update'})

        response = view(request, pk=contact.pk)
        self.assertEqual(response.status_code, 200, response.data)

        contact = Contact.objects.get(pk=response.data['id'])
        self.assertEqual(contact.__dict__, {**contact.__dict__,  **data})

    def test_update_contact_belonging_to_user_org(self):
        contact = mfactories.Contact()

        data = {'last_name': 'Lynch'}
        request = self.factory.post('', json.dumps(data), content_type='application/json')
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'post': 'update'})

        response = view(request, pk=contact.pk)
        self.assertEqual(response.status_code, 200, response.data)

        contact = Contact.objects.get(pk=response.data['id'])
        self.assertEqual(contact.__dict__, {**contact.__dict__,  **data})

    def test_update_contact_not_belonging_to_user_org(self):
        contact = mfactories.Contact()

        data = {
            'last_name': 'Lynch',
        }
        request = self.factory.post('', json.dumps(data),
                                    content_type='application/json')
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'post': 'update'})
        response = view(request, pk=contact.pk)
        self.assertEqual(response.status_code, 200, response.data)

    def test_update_contact_fails_blank_field(self):
        contact = mfactories.Contact(user_uuid=self.session['jwt_user_uuid'])

        data = {
            'first_name': 'David',
            'middle_name': 'Keith',
            'last_name': '',
        }

        request = self.factory.post('', json.dumps(data),
                                    content_type='application/json')
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'post': 'update'})

        response = view(request, pk=contact.pk)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['last_name'],
                         ['This field may not be blank.'])

    def test_update_contact_fails_invalid_phone_schema(self):
        contact = mfactories.Contact()

        data = {
            'phones': [
                {
                    'type': 'invented',
                    'number': '12345',
                },
                {
                    'type': 'mobile',
                    'number': '67890',
                },
            ],
        }
        request = self.factory.post('', data)
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'post': 'update'})
        response = view(request, pk=contact.pk)
        self.assertEqual(response.status_code, 400)

    def test_update_contact_blank_field_valid(self):
        contact = mfactories.Contact()

        data = {
            'middle_name': '',
        }
        request = self.factory.post('', json.dumps(data),
                                    content_type='application/json')
        request.user = self.user
        request.session = self.session
        view = ContactViewSet.as_view({'post': 'update'})

        response = view(request, pk=contact.pk)
        self.assertEqual(response.status_code, 200, response.data)

    def test_update_contacts_anonymoususer(self):
        request = self.factory.post('', {})
        view = ContactViewSet.as_view({'post': 'update'})
        response = view(request)
        self.assertEqual(response.status_code, 403)


class ContactDeleteViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = mfactories.User()
        self.organization_uuid = str(uuid.uuid4())
        self.session = {
            'jwt_organization_uuid': self.organization_uuid,
            'jwt_username': 'Test User',
            'jwt_user_uuid': uuid.uuid4()
        }

    def test_delete_contact(self):
        contact = mfactories.Contact()
        request = self.factory.delete('')
        request.user_uuid = self.user
        request.session = self.session

        view = ContactViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=contact.pk)

        self.assertEqual(response.status_code, 204)
        self.assertRaises(
            Contact.DoesNotExist,
            Contact.objects.get, pk=contact.pk)

    def test_delete_contact_diff_org(self):
        contact = mfactories.Contact()
        request = self.factory.delete('')
        request.user = self.user
        request.session = self.session

        view = ContactViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=contact.pk)

        self.assertEqual(response.status_code, 204)

    def test_delete_contact_diff_org_superuser(self):
        organization_other = str(uuid.uuid4())
        contact = mfactories.Contact()
        request = self.factory.delete('')

        su = mfactories.User()
        su.is_superuser = True
        su.save()

        request.user = su

        view = ContactViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=contact.pk)

        self.assertEqual(response.status_code, 204)

    def test_delete_contact_anonymous_user(self):
        contact = mfactories.Contact()
        request = self.factory.delete('')

        view = ContactViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=contact.pk)

        self.assertEqual(response.status_code, 403)
