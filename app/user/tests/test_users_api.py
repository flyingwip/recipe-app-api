from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    # the model path is
    # User.UserManager().create_user(email, password, **extra_fields)
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public/non-authenticated endpoints)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_succes(self):
        """Tests creating user with valid payload is succesfull"""

        payload = {
            'email': 'dont@think.so',
            'password': 'thisisasecret123',
            'name': 'Ferry Phonny'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_already_exists(self):
        """Test creating a user that already exists fails"""
        payload = {'email': 'me@doesexist.org',
                   'password': 'verysecret123', 'name': 'Test', }
        create_user(**payload)

        # payload = {'email': 'me1@doesexist1.org',
        #            'password': 'verysecret123gg', 'name': 'Test1', }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password should have more than 4 characters"""
        payload = {'email': 'test@somedomain.com',
                   'password': 'five', 'name': 'Test', }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
