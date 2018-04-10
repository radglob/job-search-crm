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
        "accounts/<int:user_id>/profile",
        views.ProfileView.as_view(),
        name="view_profile",
    ),
    path("accounts/login", views.login, name="login"),
    path("accounts/<int:user_id>/edit", views.edit_profile, name="edit_profile"),
    path("logout", views.logout, name="logout"),
    path("applications", views.applications, name="applications"),
    path(
        "applications/new",
        login_required(views.NewApplicationView.as_view()),
        name="new_application",
    ),
    path(
        "applications/create",
        views.create_new_application,
        name="create_new_application",
    ),
    path(
        "applications/<int:application_id>", views.application_by_id, name="application"
    ),
    path(
        "applications/<int:application_id>/events/new",
        login_required(views.NewEventView.as_view()),
        name="new_event",
    ),
    path(
        "applications/<int:application_id>/events/create",
        views.create_new_event,
        name="create_event",
    ),
    path(
        "applications/<int:application_id>/events/<int:event_id>/delete",
        views.delete_event,
        name="delete_event",
    ),
]
