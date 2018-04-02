from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from .models import CustomerProfile

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)


class IndexTests(TestCase):

    def setUp(self):
        user = User.objects.create_user(
            "joe", "joe@email.com", "password", first_name="Joe"
        )
        User.objects.create_user("jane", "jane@email.com", "password")
        CustomerProfile.objects.create(user=user)

    def test_index_with_no_user(self):
        resp = self.client.get("/")
        self.assertIn("Login", resp.content.decode())

    def test_index_with_user(self):
        self.client.login(username="joe", password="password")
        resp = self.client.get("/")
        self.assertIn("Welcome, Joe!", resp.content.decode())

    def test_index_with_user_no_profile(self):
        self.client.login(username="jane", password="password")
        resp = self.client.get("/")
        self.assertIn("Login", resp.content.decode())


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


class CreateAccountTests(TestCase):

    def setUp(self):
        User.objects.create_user("jane", "jane@email.com", "password")

    def test_create_account_success(self):
        resp = self.client.post(
            "/create_account",
            {
                "username": "joe",
                "email": "joe@email.com",
                "password": "password",
                "confirm_password": "password",
            },
        )
        self.assertEqual(resp.status_code, 302)

    def test_create_account_passwords_do_not_match(self):
        resp = self.client.post(
            "/create_account",
            {
                "username": "joe",
                "email": "joe@email.com",
                "password": "password",
                "confirm_password": "badpassword",
            },
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Passwords do not match.", resp.content.decode())

    def test_create_account_integrity_error(self):
        resp = self.client.post(
            "/create_account",
            {
                "username": "jane",
                "email": "jane@email.com",
                "password": "password",
                "confirm_password": "password",
            },
        )
        self.assertEqual(resp.status_code, 409)


class CreateProfileTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("joe", "joe@email.com", "password")

    def create_profile_success(self):
        self.client.login(username="joe", password="password")
        resp = self.client.post(
            "/create_profile",
            {
                "first_name": "Joe",
                "last_name": "Smith",
                "bio": "A little about Joe...",
                "location": "New York",
                "birth_date": datetime.today(),
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(self.user.first_name, "Joe")
