from django.db.models import Q
from django.db.utils import OperationalError

import frontend.models
from . import models


ROUND = "round"
QUESTION = "question"

question_grading_functions = {}
round_grading_functions = {}


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
                    pass

            except OperationalError:
                print("Caught operational error, assuming migration and skipping registration.")
            return function
        return decorator


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
