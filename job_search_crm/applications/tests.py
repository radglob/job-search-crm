from django.contrib.auth.models import User
from django.test import TestCase

from .models import CustomerProfile

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)


class LoginTests(TestCase):

    def setUp(self):
        user = User.objects.create_user("joe", "joe@email.com", "password")
        User.objects.create_user("jane", "jane@email.com", "password")
        CustomerProfile.objects.create(user=user)

    def test_login_with_correct_password_and_profile(self):
        resp = self.client.post("/login", {"username": "joe", "password": "password"})
        self.assertEqual(resp.status_code, 200)

    def test_login_with_incorrect_password(self):
        resp = self.client.post(
            "/login", {"username": "joe", "password": "badpassword"}
        )
        self.assertEqual(resp.status_code, 401)

    def test_login_with_correct_password_and_no_profile(self):
        resp = self.client.post("/login", {"username": "jane", "password": "password"})
        self.assertEqual(resp.status_code, 302)
