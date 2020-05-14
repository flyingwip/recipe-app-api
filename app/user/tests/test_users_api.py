from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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

    def test_create_token_for_user(self):
        """Test that a token is created for user"""
        payload = {'email': 'test@payload.com', 'password': 'thisisatest'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credential(self):
        """Test that token is not created when invalid credentials are given"""
        create_user(email='test@sometest.com', password='testpass')
        payload = {
            'email': 'test@sometest.com',
            'password': 'wrongpass'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        payload = {
            'email': 'test@sometest.com',
            'password': 'testpass'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        res = self.client.post(
            TOKEN_URL, {'email': '', 'password': 'testpass'})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUsersApiTests(TestCase):
    """Tests API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@somedomain.com',
            password='thisisverysecret123',
            name='Ferry Phonny'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profilee for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.data, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_post_me_not_allowed(self):
        """Test that post is not allowed on the me url"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for logged in users"""
        payload = {
            'name': 'new name',
            'password': 'newpass123'
        }

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['passwords']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
