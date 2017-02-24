from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User

from app import forms, models
from app import competition


def index(request):
    return render(request, "index.html")


def info(request):
    return render(request, "info.html")


def about(request):
    return render(request, "about.html")


def archive(request):
    return render(request, "archive.html")


def rules(request):
    return render(request, "rules.html")


def topics(request):
    return render(request, "topics.html")


def registration(request):
    return render(request, "registration.html")


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
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"])
            school = models.School(user=user, name=form.cleaned_data["school_name"])
            school.save()

            # Login the user and redirect
            user = auth.authenticate(username=user.get_username(), password=form.cleaned_data["password"])
            auth.login(request, user)
            return redirect('teams')

    # Render the form to the page
    return render(request, "register.html", {"form": form})


def login(request):
    """Process a login request."""

    # Check if the form is valid
    form = forms.LoginForm()
    if request.method == "POST":
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            auth.login(request, form.user)
            if request.user.is_staff:
                return redirect("grade")
            return redirect("teams")

    return render(request, "login.html", {"form": form})


@login_required
def logout(request):
    """Logout the currently logged in user."""

    auth.logout(request)
    return redirect("index")


@login_required
def teams(request):
    return render(request, "teams.html")


@login_required
def edit_team(request, pk=None):
    """Add a team to the list."""

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
        "student_helper": forms.PrettyHelper()
    })


@login_required
def remove_team(request, pk=None):
    """Remove the team."""

    if pk:
        models.Team.objects.filter(id=pk).delete()

    return redirect("teams")


@login_required
@permission_required("app.can_grade")
def grade(request):
    return render(request, "grade.html", {
        "teams": models.Team.objects.all(),
        "students": models.Student.objects.all()
    })


@login_required
@permission_required("app.can_grade")
def score(request, type, id):
    print("SCORING", type, id)