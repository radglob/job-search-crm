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

    def is_valid(self):
        valid = super().is_valid()
        if valid:
            return self.cleaned_data["min_salary"] <= self.cleaned_data["max_salary"]

        return valid


class NewEventForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea)
    date = forms.DateField(initial=timezone.now)


class CustomerProfileForm(forms.Form):
    username = forms.CharField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    birth_date = forms.DateField(required=False)
    location = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False)

    def is_valid(self):
        valid = super(CustomerProfileForm, self).is_valid()
        if not valid:
            return valid

        if self.cleaned_data["password"] == self.cleaned_data["confirm_password"]:
            return True

        else:
            return False


class CreateAccountForm(forms.Form):
    email = forms.EmailField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def is_valid(self):
        valid = super(CreateAccountForm, self).is_valid()
        if not valid:
            return valid

        if self.cleaned_data["password"] == self.cleaned_data["confirm_password"]:
            return True

        else:
            return False


class CreateProfileForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    bio = forms.CharField(widget=forms.Textarea)
    location = forms.CharField()
    birth_date = forms.DateField()
