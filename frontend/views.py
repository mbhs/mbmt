from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

from functools import partial
import datetime

from frontend import forms, models


# Short views
index = partial(render, template_name="index.html")
info = partial(render, template_name="info.html")
about = partial(render, template_name="about.html")
archive = partial(render, template_name="archive.html")
rules = partial(render, template_name="rules.html")
topics = partial(render, template_name="topics.html")
registration = partial(render, template_name="registration.html")


def allow_edit_teams():
    """Check if teams can be editing in this period."""

    return datetime.date.today() <= models.Competition.current().date_team_edit_end


def register(request):
    """The registration page for school sponsors."""

    # Assert post and form is valid
    form = forms.RegisterForm()
    if request.method == "POST":
        form = forms.RegisterForm(request.POST)
        if form.is_valid():

            # Create user and school
            user = User.objects.create_user(
                form.cleaned_data["username"],
                email=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
                first_name=form.cleaned_data["name"],
                last_name=form.cleaned_data["last_name"])
            school = models.School(user=user, name=form.cleaned_data["school_name"])
            school.save()

            # Login the user and redirect
            user = auth.authenticate(username=user.get_username(), password=form.cleaned_data["password"])
            auth.login(request, user)
            return redirect("teams")

    if request.user.is_authenticated:
        return redirect("teams")

    # Render the form to the page
    allow_registration = datetime.date.today() <= models.Competition.current().date_registration_end
    return render(request, "register.html", {"form": form, "allow_registration": allow_registration})


def login(request):
    """Process a login request."""

    # Check if the form is valid
    form = forms.LoginForm()
    if request.method == "POST":
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            auth.login(request, form.user)
            if request.user.has_perm("grading.can_grade"):
                return redirect("student_view")
            return redirect("teams")

    return render(request, "login.html", {"form": form})


@login_required
def logout(request):
    """Logout the currently logged in user."""

    auth.logout(request)
    return redirect("index")


@login_required
def display_teams(request):
    """Display current teams."""

    return render(request, "teams.html", {"allow_edit_teams": allow_edit_teams()})


@login_required
def edit_team(request, pk=None):
    """Add a team to the list."""

    if not allow_edit_teams():
        return redirect("teams")

    team = None
    students = models.Student.objects.none()

    if pk:
        team = get_object_or_404(models.Team, id=pk)
        students = team.students.all()

    team_form = forms.TeamForm(instance=team)
    student_forms = forms.StudentFormSet(queryset=students)

    # Register a team from posted data
    if request.method == "POST":
        team_form = forms.TeamForm(request.POST, instance=team)
        student_forms = forms.StudentFormSet(request.POST, queryset=students)

        # Check validity and create team
        if team_form.is_valid() and student_forms.is_valid():

            # If not editing existing
            if team:
                team.save()
            else:
                team = team_form.save(commit=False)
                team.school = request.user.school
                team.save()

            form_students = student_forms.save(commit=False)
            for student in form_students:
                student.team = team
                student.save()

            return redirect("teams")

    # Render the form view
    return render(request, "team.html", {
        "team_form": team_form,
        "student_forms": student_forms,
        "student_helper": forms.PrettyHelper()})


@login_required
def remove_team(request, pk=None):
    """Remove the team."""

    if pk:
        models.Team.objects.filter(id=pk).delete()
    return redirect("teams")
