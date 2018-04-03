from django import forms


class NewApplicationForm(forms.Form):
    company_name = forms.CharField()
    company_location = forms.CharField()
    company_sub_industry = forms.CharField()

    position_name = forms.CharField()
    is_remote = forms.BooleanField(required=False)
    min_salary = forms.IntegerField()
    max_salary = forms.IntegerField()
    tech_stack = forms.CharField()
