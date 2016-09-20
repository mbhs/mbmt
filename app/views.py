from django.shortcuts import render, redirect
from django.contrib import auth

from app import forms

import string
import random


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
            school = form.save(commit=False)
            school.code = ''.join([random.choice(string.ascii_lowercase + string.digits) for _ in range(32)])
            school.save()

            return render(request, "loggedin.html", {
                'code': school.code
            })

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