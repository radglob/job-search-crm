from django import forms
from django.utils import timezone


class NewApplicationForm(forms.Form):
    company_name = forms.CharField()
    company_location = forms.CharField()
    company_sub_industry = forms.CharField()

    position_name = forms.CharField()
    is_remote = forms.BooleanField(required=False)
    min_salary = forms.IntegerField()
    max_salary = forms.IntegerField()
    tech_stack = forms.CharField(widget=forms.Textarea)


class NewEventForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea)
    date = forms.DateField(initial=timezone.now)


class CustomerProfileForm(forms.Form):
    username = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    bio = forms.CharField(widget=forms.Textarea)
    birth_date = forms.DateField()
    location = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)


class SignupForm(forms.Form):
    email = forms.EmailField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
