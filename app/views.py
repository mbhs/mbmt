from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth

from app import forms, models


def index(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def rules(request):
    return render(request, "rules.html")


def registration(request):
    return render(request, "registration.html")


def register(request):
    form = forms.RegisterForm()

    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(form.cleaned_data['username'],
                                            email=form.cleaned_data['email'],
                                            password=form.cleaned_data['password'],
                                            first_name=form.cleaned_data['first_name'],
                                            last_name=form.cleaned_data['last_name'])

            school = models.School(user=user, name=form.cleaned_data['school_name'])
            school.save()

            user = auth.authenticate(username=user.get_username(), password=form.cleaned_data['password'])
            auth.login(request, user)

            return redirect('index')

    return render(request, "register.html", {
        'form': form
    })


def login(request):
    form = forms.LoginForm()

    if request.method == 'POST':
        form = forms.LoginForm(request.POST)

        if form.is_valid():
            auth.login(request, form.school)

            return redirect("index.html")

    return render(request, "login.html", {
        'form': form
    })