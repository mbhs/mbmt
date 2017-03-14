from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User

from app import forms, models, grading


ALLOW_REGISTRATION = False


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
    return render(request, "register.html", {"form": form, "allow_registration": ALLOW_REGISTRATION})


def login(request):
    """Process a login request."""

    # Check if the form is valid
    form = forms.LoginForm()
    if request.method == "POST":
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            auth.login(request, form.user)
            if request.user.is_staff:
                return redirect("grade_students")
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
def attendance(request):
    if request.method == "POST":
        for iid in filter(lambda x: x.isnumeric(), request.POST):
            student = models.Student.objects.filter(id=iid).first()
            if student and request.POST[iid] in ("0", "1"):
                student.attending = bool(int(request.POST[iid]))
                student.save()
        return redirect("attendance")

    students = models.Student.objects.all()
    return render(request, "attendance.html", {
        "students": zip(students[:len(students)//3+1],
                        students[len(students)//3+1:2*len(students)//3+1],
                        students[2*len(students)//3+1:])})


@login_required
@permission_required("app.can_grade")
def grade_students(request):
    return render(request, "grade_students.html", {
        "students": models.Student.objects.all()})


@login_required
@permission_required("app.can_grade")
def grade_teams(request):
    return render(request, "grade_teams.html", {
        "teams": models.Team.objects.all()})


@login_required
@permission_required("app.can_grade")
def score(request, grouping, id, round):
    """Scoring view."""

    competition = models.Competition.current()
    round = competition.rounds.filter(id=round).first()

    if grouping == "team":
        team = models.Team.objects.filter(id=id).first()
        answers = []
        question_answer = []
        for question in round.questions.order_by("order").all():
            answer = models.Answer.objects.filter(team=team, question=question).first()
            if not answer:
                answer = models.Answer(team=team, question=question)
                answer.save()
            answers.append(answer)
            question_answer.append((question, answer))

        if request.method == "POST":
            update_answers(request, answers)
            return redirect(request.META.get('HTTP_REFERER', '/'))

        return render(request, "grader.html", {
            "name": team.name,
            "division": team.get_division_display,
            "round": round,
            "question_answer": question_answer,
            "mode": "team"})

    elif grouping == "individual":
        student = models.Student.objects.filter(id=id).first()
        answers = []
        question_answer = []
        for question in round.questions.order_by("order").all():
            answer = models.Answer.objects.filter(student=student, question=question).first()
            if not answer:
                answer = models.Answer(student=student, question=question)
                answer.save()
            answers.append(answer)
            question_answer.append((question, answer))

        if request.method == "POST":
            update_answers(request, answers)
            return redirect(request.META.get('HTTP_REFERER', '/'))

        return render(request, "grader.html", {
            "name": student.name,
            "division": student.team.get_division_display,
            "round": round,
            "question_answer": question_answer,
            "mode": "student"})


def scoreboard(request):
    """Do final scoreboard calculations."""

    scores = grading.grade()
    return render(request, "scoreboard.html", {})


def update_answers(request, answers):
    """Score a team."""

    for answer in answers:
        id = str(answer.question.id)
        if id in request.POST:
            value = None if str(request.POST[id]) == "" else float(request.POST[id])
            answer.value = value
            answer.save()


@login_required
@permission_required("app.can_grade")
def shirts(request):
    """Shirt sizes view."""

    sizes = [(size[1], models.Student.objects.filter(size=i).count()) for i, size in enumerate(models.SHIRT_SIZES)]
    return render(request, "shirts.html", {"sizes": sizes})
