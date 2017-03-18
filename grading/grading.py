from django.db.models import Q
from django.db.utils import OperationalError

import frontend.models
from . import models


ROUND = "round"
QUESTION = "question"

question_grading_functions = {}
round_grading_functions = {}


def default_question(question, answer):
    """Default scoring function for a question."""

    return question.weight * answer.value


def register(level, query: Q=Q(), **filters):
    """Register a function as a grading function."""

    if level == QUESTION:
        def decorator(function):
            try:

                questions = models.Question.objects.filter(query, round__competition__active=True, **filters).all()
                for question in questions:
                    question_grading_functions[question.id] = function

            except OperationalError:
                print("Caught operational error, assuming migration and skipping registration.")
            return function
        return decorator
    elif level == ROUND:
        def decorator(function):
            try:

                rounds = models.Round.objects.filter(query, competition__active=True, **filters).all()
                for round in rounds:
                    round_grading_functions[round.id] = function

            except OperationalError:
                print("Caught operational error, assuming migration and skipping registration.")
            return function
        return decorator


def _grade_round_individual(round: models.Round):
    """Grade an individual round."""

    scores = {}
    for student in frontend.models.Student.current():
        score = 0
        for question in round.questions.all():
            answer = models.Answer.objects.filter(student=student, question=question).first()
            score += question_grading_functions[question.id](answer)
        scores[student] = score
    return scores


def _grade_round_team(round: models.Round):
    """Grade a team round."""

    scores = {}
    for team in frontend.models.Team.current():
        score = 0
        for question in round.questions.all():
            answer = models.Answer.objects.filter(team=team, question=question).first()
            if not answer:
                score += 0
                continue
            result = question_grading_functions.get(question.id, default_question)(question, answer)
            score += result or 0
        else:
            scores[team] = score
    return scores


def _grade_round(round: models.Round):
    """Grade a round for all participants."""

    if round.get_grouping_display() == "individual":
        return _grade_round_individual(round)
    elif round.get_grouping_display() == "team":
        return _grade_round_team(round)
    else:
        return None


def grade(competition=None):
    """Do grading."""

    competition = competition or models.Competition.current()
    scoreboard = {"individual": {}, "team": {}}

    individual_rounds = competition.rounds.filter(models.ROUND_GROUPINGS["individual"]).all()
    individual_correct = {r: {q: 0 for q in r.questions} for r in individual_rounds}
    for r in individual_rounds:
        for q in r.questions.all():
            individual_correct[r][q] = sum([a.value for a in models.Answer.filter(question=q).all()])

    for student in frontend.models.Student.objects.all():
        pass
