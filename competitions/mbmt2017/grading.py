"""The official MBMT 2017 grading algorithm.

The following file is intended for use as a modular plugin that
implements various grading functions for the MBMT website. In order
grading functions must be registered to either a round ID and
optionally a question ID.
"""


from django.db.models import Q

import math

# For normies, we'll let it slide
from grading.models import *
from grading.grading import *
from frontend.models import *


class MBMT2017Grader(CompetitionGrader):
    """Grader specific to MBMT 2017."""

    COMPETITION = "mbmt2017"

    def __init__(self):
        """Initialize the MBMT 2017 grader."""

        super().__init__()
        self.individual_bonus = {}
        self.register_round_grader(Q(ref="subject1"), self.subject_round_grader)
        self.register_round_grader(Q(ref="subject2"), self.subject_round_grader)
        self.register_question_grader(Q(type="estimation"), self.guts_question_grader)

    def _calculate_individual_bonuses(self, round):
        """Calculate the point bonuses for an individual round."""

        # TODO: implement individual bonus calculator
        for question in round.questions:
            self.individual_bonus[question.id] = 1

    def subject_question_grader(self, question, answer):
        """Grade an individual question."""

        # Answer value is 1 if correct, 0 if incorrect
        return question.weight * answer.value * self.individual_bonus[question.id]

    def subject_round_grader(self, round: models.Round):
        """Grade an individual subject test by round."""

        self._calculate_individual_bonuses(round)
        self.default_round_grader(round)

    def guts_question_grader(self, question, answer):
        """Grade a guts question."""

        value = 0
        if question.type == QUESTION_TYPES["correct"]:
            value = answer.value
        elif question.type == QUESTION_TYPES["estimation"]:
            e = answer.value
            a = question.answer
            value = max(0, 12 - math.log10(max(e/a, a/e)))
        return value * question.weight
