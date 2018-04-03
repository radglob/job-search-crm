from django.contrib.auth import (
    authenticate, login as auth_login, logout as auth_logout
)
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView

from .models import CustomerProfile, Application


def index(request):
    customer = None
    if not request.user.is_anonymous:
        try:
            customer = CustomerProfile.objects.get(user=request.user)
        except CustomerProfile.DoesNotExist:
            pass
    return render(request, "applications/index.html", {"customer": customer})


def signup(request):
    return render(request, "applications/signup.html")


def create_account(request):
    username, email, password, confirm_password = [
        request.POST.get(k)
        for k in ("username", "email", "password", "confirm_password")
    ]
    if password == confirm_password:
        try:
            u = User.objects.create_user(username, email=email, password=password)
            u.save()
            auth_login(request, u)
            return HttpResponseRedirect(reverse("applications:get_profile_information"))

        except IntegrityError as e:
            return render(
                request,
                "applications/signup.html",
                {"error_message": e.args[0]},
                status=409,
            )

    else:
        return render(
            request,
            "applications/signup.html",
            {"error_message": "Passwords do not match."},
            status=400,
        )


def get_profile_information(request):
    return render(request, "applications/create_profile.html")


def create_profile(request):
    first_name, last_name, bio, location, birth_date = [
        request.POST.get(k)
        for k in ("first_name", "last_name", "bio", "location", "birth_date")
    ]
    request.user.first_name = first_name
    request.user.last_name = last_name
    request.user.save()
    customer_profile = CustomerProfile.objects.create(
        user=request.user, bio=bio, location=location, birth_date=birth_date
    )
    customer_profile.save()
    return HttpResponseRedirect(reverse("applications:home"))


def login(request):
    username, password = request.POST["username"], request.POST["password"]
    user = authenticate(username=username, password=password)
    if user:
        auth_login(request, user)
    else:
        return render(
            request,
            "applications/index.html",
            {"error_message": "Username or password did not match."},
            status=401,
        )

    if not user.is_superuser:
        try:
            profile = CustomerProfile.objects.get(user=user)
        except CustomerProfile.DoesNotExist:
            return HttpResponseRedirect(reverse("applications:get_profile_information"))

    return render(request, "applications/index.html")


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse("applications:home"))


class ApplicationsView(ListView):
    template_name = "applications/applications.html"
    context_object_name = "applications_list"

    def get_queryset(self):
        customer = CustomerProfile.objects.get(user=self.request.user)
        return Application.objects.filter(applicant=customer)
