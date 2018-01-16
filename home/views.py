from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from functools import partial
import random

from . import forms, models


index = partial(render, template_name="home/index.html")
archive = partial(render, template_name="home/archive.html")
rules = partial(render, template_name="home/rules.html")
# topics = partial(render, template_name="home/topics.html")
# registration = partial(render, template_name="home/registration.html")


def info(request):
    """Render the info page with the current competition."""

    return render(request, "home/info.html", {"competition": models.Competition.current()})


def about(request):
    """Render the about page with models."""

    writers = list(models.Writer.objects.all())
    random.shuffle(writers)

    return render(request, "home/about.html", {
        "organizers": models.Organizer.objects.order_by("order").all(),
        "writers": writers})


def login(request):
    """Process a login request."""

    # Check if the form is valid
    form = forms.LoginForm()
    if request.method == "POST":
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            auth.login(request, form.user)

    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("grading:index")
        return redirect("coaches:index")

    return render(request, "home/login.html", {"form": form})


@login_required
def logout(request):
    """Logout the currently logged in user."""

    auth.logout(request)
    return redirect("home:index")
