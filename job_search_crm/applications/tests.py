from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from .models import (Application, Company, CustomerProfile, Event, Position)


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
        self.assertIn("Hi, Joe!", resp.content.decode())

    def test_index_with_user_no_profile(self):
        self.client.login(username="jane", password="password")
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 302)


class LoginTests(TestCase):

    def setUp(self):
        user = User.objects.create_user("joe", "joe@email.com", "password")
        User.objects.create_user("jane", "jane@email.com", "password")
        CustomerProfile.objects.create(user=user)

    def test_login_with_correct_password_and_profile(self):
        resp = self.client.post("/login", {"username": "joe", "password": "password"})
        self.assertEqual(resp.status_code, 302)

    def test_login_with_incorrect_password(self):
        resp = self.client.post(
            "/login", {"username": "joe", "password": "badpassword"}, follow=True
        )
        self.assertIn("Username or password did not match.", resp.content.decode())

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

    def test_create_profile_success(self):
        self.client.login(username="joe", password="password")
        resp = self.client.post(
            "/_create_profile",
            {
                "first_name": "Joe",
                "last_name": "Smith",
                "bio": "A little about Joe...",
                "location": "New York",
                "birth_date": datetime.today().strftime("%Y-%m-%d"),
            },
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Joe")
        self.assertRedirects(resp, "/applications")


class RestrictedViewsTests(TestCase):

    def setUp(self):
        users = (
            User.objects.create_user(*info)
            for info in (
                ("joe", "joe@email.com", "password"),
                ("jane", "jane@email.com", "password"),
            )
        )
        profiles = (CustomerProfile.objects.create(user=user) for user in users)
        company = Company.objects.create(
            company_name="Company Inc.", location="City, State", sub_industry="Software"
        )
        position = Position.objects.create(
            company=company,
            position_name="Software Engineer",
            min_salary=50000,
            max_salary=70000,
            is_remote=False,
            tech_stack="",
        )
        applications = [
            Application.objects.create(applicant=profile, position=position)
            for profile in profiles
        ]
        events = [
            Event.objects.create(application=application, description="Did a thing.")
            for application in applications
        ]
        self.client.login(username="joe", password="password")

    def test_user_can_see_own_application(self):
        resp = self.client.get("/applications/1")
        self.assertEqual(resp.status_code, 200)

    def test_user_cannot_see_others_applications(self):
        resp = self.client.get("/applications/2")
        self.assertEqual(resp.status_code, 302)

    def test_user_cannot_delete_other_events(self):
        resp = self.client.get("/applications/2/events/2/delete")
        event = Event.objects.get(pk=1)
        self.assertIsNotNone(event)

    def test_user_can_delete_own_events(self):
        resp = self.client.get("/applications/1/events/1/delete")
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(pk=1)

    def test_user_cannot_create_events_for_others(self):
        resp = self.client.post(
            "/applications/2/events/create",
            {"description": "Initial phone screening.", "date": datetime.today()},
        )
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(pk=3)
