from django.contrib import messages
from django.contrib.auth import (
    authenticate, login as auth_login, logout as auth_logout
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.edit import FormView

from .models import (Application, Company, CustomerProfile, Event, Position)
from .forms import NewApplicationForm, NewEventForm


def index(request):
    customer = None
    if not request.user.is_anonymous:
        try:
            customer = CustomerProfile.objects.get(user=request.user)
        except CustomerProfile.DoesNotExist:
            return HttpResponseRedirect(reverse("applications:get_profile_information"))

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


@login_required
def get_profile_information(request):
    return render(request, "applications/create_profile.html")


@login_required
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
    return HttpResponseRedirect(reverse("applications:applications"))


def login(request):
    username, password = request.POST["username"], request.POST["password"]
    user = authenticate(username=username, password=password)
    if user:
        auth_login(request, user)
    else:
        messages.error(request, "Username or password did not match.")
        return HttpResponseRedirect(reverse("applications:home"))

    if not user.is_superuser:
        try:
            profile = CustomerProfile.objects.get(user=user)
        except CustomerProfile.DoesNotExist:
            return HttpResponseRedirect(reverse("applications:get_profile_information"))

    if request.GET.get("next"):
        return HttpResponseRedirect(request.GET["next"])

    if request.GET.get("next"):
        return HttpResponseRedirect(request.GET["next"])

    return HttpResponseRedirect(reverse("applications:applications"))


@login_required
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse("applications:home"))


@login_required
def applications(request):
    try:
        customer = CustomerProfile.objects.get(user=request.user)
        applications = Application.objects.filter(applicant=customer)
        return render(
            request,
            "applications/applications.html",
            {"applications_list": applications},
        )

    except CustomerProfile.DoesNotExist:
        return HttpResponseRedirect(reverse("applications:get_profile_information"))


class NewApplicationView(FormView):
    template_name = "applications/new_application.html"
    form_class = NewApplicationForm
    success_url = "/applications"


@login_required
def create_new_application(request):
    form = NewApplicationForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
    company, __ = Company.objects.get_or_create(
        company_name=data["company_name"],
        defaults={
            "location": data["company_location"],
            "sub_industry": data["company_sub_industry"],
        },
    )
    position, __ = Position.objects.get_or_create(
        company=company,
        position_name=data["position_name"],
        defaults={
            "is_remote": data.get("is_remote", False),
            "min_salary": data["min_salary"],
            "max_salary": data["max_salary"],
            "tech_stack": data["tech_stack"],
        },
    )
    application, created = Application.objects.get_or_create(
        applicant=request.user.customerprofile, position=position
    )
    if not created:
        messages.error(request, "This application already exists.")
        return HttpResponseRedirect(reverse("applications:applications"))

    else:
        messages.success(request, "New application created!")
        return HttpResponseRedirect(reverse("applications:applications"))


@login_required
def application_by_id(request, application_id):
    try:
        application = Application.objects.get(pk=application_id)
        if application.applicant.user.id != request.user.id:
            return HttpResponseRedirect(reverse("applications:applications"))

        return render(
            request,
            "applications/application_details.html",
            {"application": application},
        )

    except Application.DoesNotExist:
        return HttpResponseRedirect(reverse("applications:applications"))


class NewEventView(FormView):
    template_name = "applications/new_event.html"
    form_class = NewEventForm
    success_url = "/applications"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["application_id"] = self.kwargs["application_id"]
        return context


@login_required
def create_new_event(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    if application.applicant.user.id == request.user.id:
        event = Event.objects.create(
            application=application,
            description=request.POST["description"],
            date=request.POST["date"],
        )
        event.save()
        messages.success(request, "New event added.")
        return HttpResponseRedirect(
            reverse(
                "applications:application", kwargs={"application_id": application_id}
            )
        )

    else:
        return HttpResponseRedirect(reverse("applications:applications"))


@login_required
def delete_event(request, application_id, event_id):
    event = Event.objects.get(pk=event_id)
    if event.application.applicant.user.id == request.user.id:
        event.delete()
    return HttpResponseRedirect(
        reverse("applications:application", kwargs={"application_id": application_id})
    )
