"""The official MBMT 2017 grading algorithm.

The following file is intended for use as a modular plugin that
implements various grading functions for the MBMT website. In order
grading functions must be registered to either a round ID and
optionally a question ID.
"""


from django.db.models import Q

import math

# For normies, we'll let it slide
import grading.models as g
from grading.grading import CompetitionGrader


# Redefine useful constants
from grading.models import CORRECT, ESTIMATION
SUBJECT1 = "subject1"
SUBJECT2 = "subject2"
GUTS = "guts"
TEAM = "team"


class Grader(CompetitionGrader):
    """Grader specific to MBMT 2017."""

    COMPETITION = "mbmt2017"

    LAMBDA = 0.52

    def __init__(self):
        """Initialize the MBMT 2017 grader."""

        super().__init__()
        self.individual_bonus = {}
        self.register_round_grader(
            Q(ref=SUBJECT1) | Q(ref=SUBJECT2),
            self.subject_round_grader)
        self.register_question_grader(
            Q(round__ref=SUBJECT1),
            self.subject1_question_grader)
        self.register_question_grader(
            Q(round__ref=SUBJECT2),
            self.subject2_question_grader)
        self.register_question_grader(
            Q(type=ESTIMATION),
            self.guts_question_grader)

    def _calculate_individual_bonuses(self, round1, round2):
        """Calculate the point bonuses for an individual round."""

        self.individual_bonus = {}

        factors = {}
        for i, round in enumerate((round1, round2)):
            for question in round.questions.all():
                for answer in g.Answer.objects.filter(question=question).all():

                    # Ignores people whose grading view is not opened
                    division = answer.student.team.division
                    subject = answer.student.subject1 if i == 0 else answer.student.subject2

                    if division not in factors:
                        factors[division] = {}
                        self.individual_bonus[division] = {}
                    if subject not in factors[division]:
                        factors[division][subject] = {}
                        self.individual_bonus[division][subject] = {}
                    if question.id not in factors[division][subject]:
                        factors[division][subject][question.id] = [0, 0]  # Correct, total
                    factors[division][subject][question.id][0] += answer.value or 0
                    factors[division][subject][question.id][1] += 1

        for division in factors:
            for subject in factors[division]:
                for question in factors[division][subject]:
                    correct, total = factors[division][subject][question]
                    self.individual_bonus[division][subject] = (
                        0 if correct == 0 else self.LAMBDA * math.log(total / correct))

    def subject1_question_grader(self, question, answer):
        """Grade an individual question."""

        # Answer value is 1 if correct, 0 if incorrect
        return (question.weight * answer.value) #*
                #self.individual_bonus[answer.student.team.division][answer.student.subject1])

    def subject2_question_grader(self, question, answer):
        """Grade an individual question."""

        # Answer value is 1 if correct, 0 if incorrect
        return (question.weight * answer.value *
                self.individual_bonus[answer.student.team.division][answer.student.subject2])

    def subject_round_grader(self, round: g.Round):
        """Grade an individual subject test by round."""

        return self.default_round_grader(round)

    def guts_question_grader(self, question, answer):
        """Grade a guts question."""

        value = 0
        if question.type == g.QUESTION_TYPES["correct"]:
            value = answer.value
        elif question.type == g.QUESTION_TYPES["estimation"]:
            e = answer.value
            a = question.answer
            value = max(0, 12 - math.log10(max(e/a, a/e)))
        return value * question.weight

    def grade_competition(self, competition):
        """Grade the entire competition."""

        subject1 = competition.rounds.filter(ref="subject1").first()
        subject2 = competition.rounds.filter(ref="subject2").first()
        self._calculate_individual_bonuses(subject1, subject2)
        super().grade_competition(competition)
