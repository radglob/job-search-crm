from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase

from .models import (Application, Company, CustomerProfile, Event, Position)


class IndexTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(
            "joe", "joe@email.com", "password", first_name="Joe"
        )
        User.objects.create_user("jane", "jane@email.com", "password")
        CustomerProfile.objects.create(user=user)

    def test_index_get_with_no_user(self):
        resp = self.client.get("/")
        self.assertIn("Login", resp.content.decode())

    def test_index_get_with_user(self):
        self.client.login(username="joe", password="password")
        resp = self.client.get("/")
        self.assertIn("Joe", resp.content.decode())

    def test_index_get_with_user_no_profile(self):
        self.client.login(username="jane", password="password")
        resp = self.client.get("/")
        self.assertRedirects(resp, "/accounts/register/profile")

    def test_index_post(self):
        resp = self.client.post("/", {"test": "test"})
        self.assertEqual(resp.status_code, 405)


class CreateAccountTests(TransactionTestCase):

    def test_create_account_get(self):
        resp = self.client.get("/accounts/register")
        self.assertIn("Register Account", resp.content.decode())

    def test_create_account_post_success(self):
        resp = self.client.post(
            "/accounts/register",
            {
                "username": "joe",
                "email": "joe@email.com",
                "password": "goodpassword",
                "confirm_password": "goodpassword",
            },
        )
        self.assertRedirects(resp, "/accounts/register/profile")

    def test_create_account_passwords_do_not_match(self):
        resp = self.client.post(
            "/accounts/register",
            {
                "username": "joe",
                "email": "joe@email.com",
                "password": "password",
                "confirm_password": "badpassword",
            },
        )
        self.assertIn("Passwords do not match.", resp.content.decode())
        self.assertEqual(resp.status_code, 400)

    def test_create_account_integrity_error(self):
        User.objects.create_user("jane", "jane@email.com", "password")
        resp = self.client.post(
            "/accounts/register",
            {
                "username": "jane",
                "email": "jane@email.com",
                "password": "badpassword",
                "confirm_password": "badpassword",
            },
        )
        self.assertIn(
            "A user with this username already exists.", resp.content.decode()
        )
        self.assertEqual(resp.status_code, 400)


class CreateProfileTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("joe", "joe@email.com", "password")

    def test_get_create_profile_view(self):
        self.client.login(username="joe", password="password")
        resp = self.client.get("/accounts/register/profile")
        self.assertIn("Create customer profile", resp.content.decode())

    def test_get_create_profile_view_requires_login(self):
        resp = self.client.get("/accounts/register/profile")
        self.assertRedirects(resp, "/?next=/accounts/register/profile")

    def test_post_create_profile_success(self):
        self.client.login(username="joe", password="password")
        resp = self.client.post(
            "/accounts/register/profile",
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


class LoginTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user("joe", "joe@email.com", "password")
        User.objects.create_user("jane", "jane@email.com", "password")
        CustomerProfile.objects.create(user=user)

    def test_login_with_correct_password_and_profile(self):
        resp = self.client.post(
            "/accounts/login", {"username": "joe", "password": "password"}
        )
        self.assertEqual(resp.status_code, 302)

    def test_login_with_incorrect_password(self):
        resp = self.client.post(
            "/accounts/login",
            {"username": "joe", "password": "badpassword"},
            follow=True,
        )
        self.assertIn("Username or password did not match.", resp.content.decode())

    def test_login_with_correct_password_and_no_profile(self):
        resp = self.client.post(
            "/accounts/login", {"username": "jane", "password": "password"}
        )
        self.assertEqual(resp.status_code, 302)


class RestrictedViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

    def setUp(self):
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
        resp = self.client.delete("/applications/1/events/1")
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(pk=1)

    def test_user_cannot_create_events_for_others(self):
        resp = self.client.post(
            "/applications/2/events/create",
            {"description": "Initial phone screening.", "date": datetime.today()},
        )
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(pk=3)


class ProfileViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(
            "joe", "joe@email.com", "password", first_name="Joe", last_name="Smith"
        )
        CustomerProfile.objects.create(
            user=user, bio="A simple man", location="Baltimore, MD"
        )

    def test_get_profile_view(self):
        self.client.login(username="joe", password="password")
        resp = self.client.get("/accounts/profile")
        self.assertIn("Profile", resp.content.decode())

    def test_user_can_edit_profile(self):
        self.client.login(username="joe", password="password")
        self.client.post(
            "/accounts/profile",
            {
                "first_name": "John",
                "last_name": "Doe",
                "bio": "Trying to be anonymous.",
            },
        )
        user = User.objects.get(pk=1)
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")

        profile = CustomerProfile.objects.get(pk=1)
        self.assertEqual(profile.bio, "Trying to be anonymous.")

    def test_user_can_change_password(self):
        self.client.login(username="joe", password="password")
        self.client.post(
            "/accounts/profile",
            {"password": "better_password", "confirm_password": "better_password"},
        )
        user = User.objects.get(pk=1)
        self.assertTrue(user.check_password("better_password"))

    def test_password_will_not_be_changed_if_matches_old_password(self):
        self.client.login(username="joe", password="password")
        self.client.post(
            "/accounts/profile",
            {"password": "password", "confirm_password": "password"},
        )
        user = User.objects.get(pk=1)
        self.assertTrue(user.check_password("password"))

    def test_password_and_confirm_password_must_match(self):
        self.client.login(username="joe", password="password")
        self.client.post(
            "/accounts/profile",
            {"password": "better_password", "confirm_password": "better_pass"},
        )
        user = User.objects.get(pk=1)
        self.assertTrue(user.check_password("password"))

    def test_no_info_changes_if_password_change_fails(self):
        self.client.login(username="joe", password="password")
        self.client.post(
            "/accounts/profile",
            {
                "first_name": "John",
                "password": "new_password",
                "confirm_password": "new_pass",
            },
        )
        user = User.objects.get(pk=1)
        self.assertEquals(user.first_name, "Joe")


class ApplicationsViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user("jane", "jane@email.com", "password")
        user = User.objects.create_user("joe", "joe@email.com", "password")
        CustomerProfile.objects.create(
            user=user, bio="A simple man", location="Baltimore, MD"
        )

    def test_get_applications_cannot_be_seen_without_profile(self):
        self.client.login(username="jane", password="password")
        resp = self.client.get("/applications")
        self.assertRedirects(resp, "/accounts/register/profile")

    def test_get_applications_can_visible_with_profile(self):
        self.client.login(username="joe", password="password")
        resp = self.client.get("/applications")
        self.assertIn("You have no open applications right now.", resp.content.decode())

    def test_get_applications_with_open_applications(self):
        user = User.objects.get(username="joe")
        profile = CustomerProfile.objects.get(user=user)
        company = Company.objects.create(
            company_name="Company, Inc.",
            location="Baltimore, MD",
            sub_industry="Widgets",
        )
        position = Position.objects.create(
            company=company,
            position_name="Software Engineer",
            is_remote=False,
            min_salary=50000,
            max_salary=60000,
            tech_stack="Python",
        )
        Application.objects.create(applicant=profile, position=position)

        self.client.login(username="joe", password="password")
        resp = self.client.get("/applications")
        self.assertIn(
            "Application to Software Engineer at Company, Inc.: Open",
            resp.content.decode(),
        )

    def test_get_applications_with_closed_applications(self):
        user = User.objects.get(username="joe")
        profile = CustomerProfile.objects.get(user=user)
        company = Company.objects.create(
            company_name="Company, Inc.",
            location="Baltimore, MD",
            sub_industry="Widgets",
        )
        position = Position.objects.create(
            company=company,
            position_name="Software Engineer",
            is_remote=False,
            min_salary=50000,
            max_salary=60000,
            tech_stack="Python",
        )
        Application.objects.create(
            applicant=profile, position=position, status="Declined by employer"
        )

        self.client.login(username="joe", password="password")
        resp = self.client.get("/applications")
        self.assertIn("You have no open applications right now.", resp.content.decode())


class NewApplicationViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user("joe", "joe@email.com", "password")
        CustomerProfile.objects.create(
            user=user, bio="Something interesting", location="Baltimore, MD"
        )
        company = Company.objects.create(
            company_name="Company, Inc.",
            location="Baltimore, MD",
            sub_industry="Widgets",
        )
        position = Position.objects.create(
            company=company,
            position_name="Software Engineer",
            is_remote=False,
            min_salary=50000,
            max_salary=60000,
            tech_stack="Python",
        )

    def test_get_new_applications_view_requires_login(self):
        resp = self.client.get("/applications/new")
        self.assertRedirects(resp, "/?next=/applications/new")

    def test_get_new_applications_view_returns_form(self):
        self.client.login(username="joe", password="password")
        resp = self.client.get("/applications/new")
        self.assertIn("New Application", resp.content.decode())

    def test_post_new_applications_view_creates_application(self):
        self.client.login(username="joe", password="password")
        resp = self.client.post(
            "/applications/new",
            {
                "company_name": "Company, Inc.",
                "company_location": "Baltimore, MD",
                "company_sub_industry": "Widgets",
                "position_name": "Software Engineer",
                "is_remote": False,
                "min_salary": 50000,
                "max_salary": 60000,
                "tech_stack": "Python",
            },
        )
        applications = Application.objects.all()
        self.assertEquals(len(applications), 1)

    def test_post_new_applications_view_min_salary_must_be_less_than_max(self):
        self.client.login(username="joe", password="password")
        resp = self.client.post(
            "/applications/new",
            {
                "company_name": "Company, Inc.",
                "company_location": "Baltimore, MD",
                "company_sub_industry": "Widgets",
                "position_name": "Software Engineer",
                "is_remote": False,
                "min_salary": 70000,
                "max_salary": 60000,
                "tech_stack": "Python",
            },
        )
        applications = Application.objects.all()
        self.assertEquals(len(applications), 0)


class ApplicationByIdViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user("joe", "joe@email.com", "password")
        profile = CustomerProfile.objects.create(
            user=user, bio="Something else", location="Baltimore, MD"
        )
        company = Company.objects.create(
            company_name="Company, Inc.",
            location="Baltimore, MD",
            sub_industry="Widgets",
        )
        position = Position.objects.create(
            company=company,
            position_name="Software Engineer",
            is_remote=False,
            min_salary=50000,
            max_salary=60000,
            tech_stack="Python",
        )
        application = Application.objects.create(applicant=profile, position=position)

    def test_get_application_by_id_view_requires_login(self):
        resp = self.client.get("/applications/1")
        self.assertRedirects(resp, "/?next=/applications/1")

    def test_get_application_by_id_shows_application_details(self):
        self.client.login(username="joe", password="password")
        resp = self.client.get("/applications/1")
        self.assertIn("Application to Company, Inc.", resp.content.decode())

    def test_post_application_by_id_not_allowed(self):
        self.client.login(username="joe", password="password")
        resp = self.client.post("/applications/1")
        self.assertEquals(resp.status_code, 405)
