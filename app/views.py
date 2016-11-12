from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User

from app import forms, models


def index(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def rules(request):
    return render(request, "rules.html")


def topics(request):
    return render(request, "topics.html")


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
            auth.login(request, form.user)

            return redirect('index')

    return render(request, "login.html", {
        'form': form
    })


def logout(request):
    auth.logout(request)

    return redirect('index')


@login_required
def teams(request):
    return render(request, "teams.html")


@login_required
def add_team(request):
    team_form = forms.TeamForm()
    student_forms = forms.StudentFormSet()

    if request.method == 'POST':
        team_form = forms.TeamForm(request.POST)
        student_forms = forms.StudentFormSet(request.POST)

        if team_form.is_valid() and student_forms.is_valid():
            team = team_form.save(commit=False)
            team.school = request.user.school
            team.save()

            students = student_forms.save(commit=False)

            for student in students:
                student.team = team
                student.save()

            return redirect('teams')

    return render(request, "team.html", {
        'team_form': team_form,
        'student_helper': forms.PrettyHelper(),
        'student_forms': student_forms
    })


@login_required
@permission_required('app.can_grade')
def grade(request):
    return render(request, "grade.html", {
        'teams': models.Team.objects.all(),
        'students': models.Student.objects.all()
    })


@login_required
@permission_required('app.can_grade')
def score(request, type, id):
    print("SCORING", type, id)