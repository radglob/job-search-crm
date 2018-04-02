from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(null=True, blank=True)


class Company(models.Model):
    company_name = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    sub_industry = models.CharField(max_length=50)

    def __str__(self):
        return self.company_name


class Position(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    position_name = models.CharField(max_length=50)
    is_remote = models.BooleanField()
    min_salary = models.IntegerField()
    max_salary = models.IntegerField()
    tech_stack = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return " at ".join((self.position_name, self.company.company_name))
