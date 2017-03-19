from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

import frontend.models
from . import models


@login_required
@permission_required("app.can_grade")
def view_students(request):
    return render(request, "grade.students.html", {
        "students": frontend.models.Student.objects.all()})


@login_required
@permission_required("app.can_grade")
def view_teams(request):
    return render(request, "grade.teams.html", {
        "teams": frontend.models.Team.objects.all()})


@login_required
@permission_required("app.can_grade")
def score(request, grouping, id, round):
    """Scoring view."""

    competition = models.Competition.current()
    round = competition.rounds.filter(ref=round).first()

    if grouping == "team":
        return score_team(request, id, round)
    elif grouping == "individual":
        return score_individual(request, id, round)


def score_team(request, id, round):
    """Scoring view for a team."""

    # Iterate questions and get answers
    team = frontend.models.Team.objects.filter(id=id).first()
    answers = []
    question_answer = []
    for question in round.questions.order_by("order").all():
        answer = models.Answer.objects.filter(team=team, question=question).first()
        if not answer:
            answer = models.Answer(team=team, question=question)
            answer.save()
        answers.append(answer)
        question_answer.append((question, answer))

    # Update the answers
    if request.method == "POST":
        update_answers(request, answers)
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Render the grading view
    return render(request, "grader.html", {
        "name": team.name,
        "division": team.get_division_display,
        "round": round,
        "question_answer": question_answer,
        "mode": "team"})


def score_individual(request, id, round):
    """Scoring view for an individual."""

    # Iterate questions and get answers
    student = frontend.models.Student.objects.filter(id=id).first()
    answers = []
    question_answer = []
    for question in round.questions.order_by("order").all():
        answer = models.Answer.objects.filter(student=student, question=question).first()
        if not answer:
            answer = models.Answer(student=student, question=question)
            answer.save()
        answers.append(answer)
        question_answer.append((question, answer))

    # Update the answers
    if request.method == "POST":
        update_answers(request, answers)
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Render the grading view
    return render(request, "grader.html", {
        "name": student.name,
        "division": student.team.get_division_display,
        "round": round,
        "question_answer": question_answer,
        "mode": "student"})


def update_answers(request, answers):
    """Update the answers to a round by an individual or group."""

    for answer in answers:
        id = str(answer.question.id)
        if id in request.POST:
            value = None if str(request.POST[id]) == "" else float(request.POST[id])
            if answer.value != value:
                answer.value = value
                answer.save()


@login_required
@permission_required("app.can_grade")
def shirts(request):
    """Shirt sizes view."""

    sizes = [(size[1], frontend.models.Student.objects.filter(size=i).count())
             for i, size in enumerate(frontend.models.SHIRT_SIZES)]
    return render(request, "shirts.html", {"sizes": sizes})


@login_required
@permission_required("app.can_grade")
def attendance(request):
    """Display the attendance page."""

    # If data is posted
    if request.method == "POST":
        attendance_post(request)
        return redirect("attendance")

    # Format students into nice columns
    students = frontend.models.Student.objects.all()
    count = request.GET.get("columns", 4)
    columns = zip(*(students[(i*len(students))//count:((i+1)*len(students))//count+1] for i in range(count)))
    return render(request, "attendance.html", {"students": columns})


def attendance_post(request):
    """Handle post data from the attendance.

    There's some degree of weirdness here, as check boxes don't post
    anything unless they're checked. To prevent this, hidden inputs
    are included for every check box with the absent value. The final
    result is accessed by getting the list of posted values and
    checking if present is in it. To minimize saves, only students
    whose attendance has changed are modified.
    """

    # Iterate post data for numeric entires
    for iid in filter(lambda x: x.isnumeric(), request.POST):
        student = frontend.models.Student.objects.filter(id=iid).first()

        # Check if student, check present or absent
        if student:
            values = request.POST.getlist(iid)
            if "absent" in values:

                # Modify in database
                attending = "present" in request.POST.getlist(iid)
                if student.attending != attending:
                    student.attending = attending
                    student.save()


def scoreboard(request):
    """Do final scoreboard calculations."""

    scores = grading.grade()
    return render(request, "scoreboard.html", {})


def live(request, round):
    """Get the live guts scoreboard."""

    if round == "guts":
        scores = grading.grade("guts")
        return render("live_guts.html", {"scores": scores})
    else:
        return redirect("scoreboard")

