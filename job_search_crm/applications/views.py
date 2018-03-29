from django.contrib.auth import login as auth_login
from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import CustomerProfile


def index(request):
    if not isinstance(request.user, AnonymousUser):
        try:
            customer = CustomerProfile.objects.get(user=request.user)
        except CustomerProfile.DoesNotExist:
            customer = None
    else:
        customer = None
    return render(request, 'applications/index.html', {'customer': customer})

def signup(request):
    return render(request, 'applications/signup.html')

def create_account(request):
    username, email, password, confirm_password = [
        request.POST.get(k) for k in 
        ('username', 'email', 'password', 'confirm_password')
    ]
    if password == confirm_password:
        u = User.objects.create_user(username, email=email, password=password)
        u.save()
        auth_login(request, u)
        return HttpResponseRedirect(
                reverse('applications:get_profile_information')) 

def get_profile_information(request):
    return render(request, 'applications/create_profile.html')
        

def create_profile(request):
    first_name, last_name, bio, location, birth_date = [
        request.POST.get(k) for k in 
        ('first_name', 'last_name', 'bio', 'location', 'birth_date')]
    request.user.first_name = first_name
    request.user.last_name = last_name
    request.user.save()
    customer_profile = CustomerProfile.objects.create(
        user=request.user,
        bio=bio,
        location=location,
        birth_date=birth_date)
    customer_profile.save()
    return HttpResponseRedirect(reverse('applications:home'))

def login(request):
    __, username, password = request.POST.values()
    return HttpResponse('{}, {}'.format(username, password))
