from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.last_name + ", " + self.user.first_name


class Company(models.Model):
    company_name = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    sub_industry = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Companies"

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


APPLICATION_STATUS_CHOICES = (
    ("0", "Open"),
    ("1", "Declined by employer"),
    ("2", "Offer extended"),
    ("3", "Position accepted"),
)


class Application(models.Model):
    applicant = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True)
    status = models.CharField(
        max_length=50, choices=APPLICATION_STATUS_CHOICES, default="Open"
    )

    def __str__(self):
        return "Application to {}: {}".format(self.position, self.status)


class Event(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    description = models.TextField(max_length=500, null=False)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return "{} for {}".format(self.description, self.application)
