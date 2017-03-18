"""The official MBMT 2017 grading algorithm.

The following file is intended for use as a modular plugin that
implements various grading functions for the MBMT website. In order
grading functions must be registered to either a round ID and
optionally a question ID.
"""


import math

# For normies, we'll let it slide
from grading.models import *
from grading.grading import *
from frontend.models import *


individual_bonus_cache = {}


def calculate_individual_bonuses(round):
    """Calculate the point bonuses for an individual round."""

    for question in round.questions:
        pass


@register(QUESTION, Q(round__ref="subject1") | Q(round__ref="subject2"))
def grade_subject_test_question(question, answer):
    """Grade an individual question."""

    pass


@register(ROUND, Q(ref="subject1") | Q(ref="subject2"))
def grade_subject_tests(scores):
    """Grade an individual subject test by round."""

    pass


@register(ROUND, ref="guts")
def grade_guts(questions, answers):
    """Grade guts rounds for all teams."""

    competition = competition or Competition.current()
    guts = competition.rounds.filter(id="guts")
    scores = {}

    for team in Team.objects.all():
        score = 0
        for question in guts.questions:

            answer = Answer.objects.filter(team=team, question=question).first()
            if not answer:
                score = None
                break

            value = 0
            if question.type == QUESTION_TYPES["correct"]:
                value = answer.value
            elif question.type == QUESTION_TYPES["estimation"]:
                e = answer.value
                a = question.answer
                value = max(0, 12 - math.log10(max(e/a, a/e)))

            score += value * question.weight

        try:
            scores[team.division][team.name] = score
        except IndexError:
            scores[team.division] = {}

    for division in scores:
        scores[division] = list(sorted(((team, scores[division][team]) for team in scores[division])))

    return scores
