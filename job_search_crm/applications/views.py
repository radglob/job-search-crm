from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import (
    authenticate, login as auth_login, logout as auth_logout
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import FormView

from .models import (Application, Company, CustomerProfile, Event, Position)
from .forms import (
    CreateAccountForm,
    CreateProfileForm,
    CustomerProfileForm,
    NewApplicationForm,
    NewEventForm,
)


class IndexView(TemplateView):
    template_name = "applications/index.html"

    def get(self, request):
        customer = None
        if not request.user.is_anonymous:
            try:
                customer = CustomerProfile.objects.get(user=request.user)
            except CustomerProfile.DoesNotExist:
                return HttpResponseRedirect(reverse("applications:create_profile"))

        return render(request, "applications/index.html", {"customer": customer})

    def post(self, request):
        return render(request, "applications/405.html", status=405)


class CreateAccountView(FormView):
    template_name = "applications/signup.html"
    form_class = CreateAccountForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username, email, password = [
                form.cleaned_data.get(k) for k in ("username", "email", "password")
            ]
            try:
                validate_password(password)
                u = User.objects.create_user(username, email, password)
                u.save()
                auth_login(request, u)
                return HttpResponseRedirect(reverse("applications:create_profile"))

            except IntegrityError:
                messages.error(request, "A user with this username already exists.")
                return render(request, self.template_name, {"form": form}, status=400)

            except ValidationError:
                messages.error(request, "This password is not valid.")
                return render(request, self.template_name, {"form": form}, status=400)

        else:
            messages.error(request, "Passwords do not match.")
            return render(request, self.template_name, {"form": form}, status=400)


class CreateProfileView(FormView):
    template_name = "applications/create_profile.html"
    form_class = CreateProfileForm

    def get(self, request):
        form = self.form_class()
        return render(request, "applications/create_profile.html", {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            first_name, last_name, bio, location, birth_date = [
                form.cleaned_data.get(k)
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
            return HttpResponseRedirect(reverse("applications:create_profile"))

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
        return HttpResponseRedirect(reverse("applications:create_profile"))


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


def edit_profile(request, user_id):
    user_keys = ("first_name", "last_name", "email")
    profile_keys = ("bio", "birth_date", "location")
    password_keys = ("password", "confirm_password")

    for k in user_keys:
        value = request.POST.get(k)
        if value:
            setattr(request.user, k, value)

    for k in profile_keys:
        value = request.POST.get(k)
        if value:
            setattr(request.user.customerprofile, k, value)

    password_values = (password, confirm_password) = [
        request.POST.get(k) for k in password_keys
    ]
    if all(password_values):
        try:
            validate_password(password)
        except ValidationError:
            messages.error(request, "This password isn't strong enough.")
            return HttpResponseRedirect(
                reverse(
                    "applications:view_profile", kwargs={"user_id": request.user.id}
                )
            )

        if request.user.check_password(password):
            messages.error(request, "This is your current password.")
            return HttpResponseRedirect(
                reverse(
                    "applications:view_profile", kwargs={"user_id": request.user.id}
                )
            )

        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return HttpResponseRedirect(
                reverse(
                    "applications:view_profile", kwargs={"user_id": request.user.id}
                )
            )

        else:
            request.user.set_password(password)

    request.user.save()
    request.user.customerprofile.save()

    messages.success(request, "Profile updated successfully.")
    return HttpResponseRedirect(
        reverse("applications:view_profile", kwargs={"user_id": request.user.id})
    )


class ProfileView(FormView):
    template_name = "applications/profile.html"
    form_class = CustomerProfileForm

    def get_initial(self):
        initial = super().get_initial()
        initial["username"] = self.request.user.username
        initial["first_name"] = self.request.user.first_name
        initial["last_name"] = self.request.user.last_name
        initial["email"] = self.request.user.email
        initial["bio"] = self.request.user.customerprofile.bio
        initial["birth_date"] = self.request.user.customerprofile.birth_date
        initial["location"] = self.request.user.customerprofile.location
        return initial
