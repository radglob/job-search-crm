from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = "applications"
urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    path("accounts/register", views.CreateAccountView.as_view(), name="create_account"),
    path(
        "accounts/register/profile",
        login_required(views.CreateProfileView.as_view()),
        name="create_profile",
    ),
    path(
        "accounts/profile",
        login_required(views.ProfileView.as_view()),
        name="view_profile",
    ),
    path("accounts/login", views.login, name="login"),
    path("accounts/logout", views.logout, name="logout"),
    path("applications", views.applications, name="applications"),
    path(
        "applications/new",
        login_required(views.NewApplicationView.as_view()),
        name="new_application",
    ),
    path(
        "applications/<int:application_id>",
        login_required(views.ApplicationDetailView.as_view()),
        name="application",
    ),
    path(
        "applications/<int:application_id>/events",
        login_required(views.EventsView.as_view()),
        name="new_event",
    ),
    path(
        "applications/<int:application_id>/events/<int:event_id>",
        login_required(views.EventByIdView.as_view()),
        name="delete_event",
    ),
]
