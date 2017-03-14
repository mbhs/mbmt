import json
from app import models


grading = {}
bonus_cache = {}


def for_round(*names):
    def decorator(function):
        for name in names:
            grading[name] = function
        return function
    return decorator


def calculate_bonuses(round):
    """Calculate the point bonuses for an individual round."""

    for question in round.questions:
        pass


def grade_subject_test(round, student):
    """Grade an individual subject test by round."""

    score = 0
    for question in round.questions:
        answer = models.Answer.objects.filter(question=question, student=student).first()
        if not answer:
            return None
        if question.type == models.QUESTION_TYPES["correct"]:
            score += 1


@for_round("subject1", "subject2")
def grade_subject_tests(competition=None):
    """Grade all individual scores."""




def grade(competition=None):
    """Do grading."""

    competition = competition or models.Competition.current()
    scoreboard = {"individual": {}, "team": {}}

    individual_rounds = competition.rounds.filter(models.ROUND_GROUPINGS["individual"]).all()
    individual_correct = {r: {q: 0 for q in r.questions} for r in individual_rounds}
    for r in individual_rounds:
        for q in r.questions.all():
            individual_correct[r][q] = sum([a.value for a in models.Answer.filter(question=q).all()])

    for student in models.Student.objects.all():
        pass
