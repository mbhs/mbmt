"""The official MBMT 2017 grading algorithm.

The following file is intended for use as a modular plugin that
implements various grading functions for the MBMT website. In order
grading functions must be registered to either a round ID and
optionally a question ID.
"""


from django.db.models import Q

import math
import statistics

import scipy.optimize

import grading.models as g
import frontend.models as f
from grading.grading import CompetitionGrader, ChillDictionary, cached
from grading.models import CORRECT, ESTIMATION


SUBJECT1 = "subject1"
SUBJECT2 = "subject2"
GUTS = "guts"
TEAM = "team"


class Grader(CompetitionGrader):
    """Grader specific to MBMT 2017."""

    LAMBDA = 0.52

    cache = {}

    def __init__(self, competition: g.Competition):
        """Initialize the MBMT 2017 grader."""

        super().__init__(competition)
        self.individual_bonus = {}
        self.individual_exponents = {}

        # Question graders
        self.register_question_grader(
            Q(round__ref=SUBJECT1),
            self.subject1_question_grader)
        self.register_question_grader(
            Q(round__ref=SUBJECT2),
            self.subject2_question_grader)
        self.register_question_grader(
            Q(type=ESTIMATION),
            self.guts_question_grader)

    def _calculate_individual_modifiers(self, round1, round2):
        """Calculate the point bonuses for an individual round."""

        self.individual_bonus = {}

        factors = ChillDictionary()
        for i, round in enumerate((round1, round2)):
            for question in round.questions.all():
                for answer in g.Answer.objects.filter(question=question).all():

                    # Ignores people whose grading view is not opened
                    division = answer.student.team.division
                    subject = answer.student.subject1 if i == 0 else answer.student.subject2

                    # Set atomic factor to correct and total values
                    if question not in factors[division][subject]:
                        factors[division][subject][question] = [0, 0]  # Correct, total
                    factors[division][subject][question][0] += answer.value or 0
                    factors[division][subject][question][1] += 1

        for division in factors:
            for subject in factors[division]:
                for question in factors[division][subject]:
                    correct, total = factors[division][subject][question]
                    self.individual_bonus[division][subject] = (
                        self.LAMBDA * math.log(total / (correct+1)))

    def _power_average_partial(self, scores):
        """Return a partial that averages scores raised to a power."""

        def power_average(d):
            return 1.0/len(scores) * sum(pow(score, d) for score in scores) - 0.375
        return power_average

    def _calculate_individual_exponent(self, scores):
        """Determines the exponent for an individual subject test."""

        return scipy.optimize.newton(self._power_average_partial(scores), 1, tol=0.0001, maxiter=1000)

    def subject1_question_grader(self, question, answer):
        """Grade an individual question."""

        return (question.weight * (answer.value or 0) *
                self.individual_bonus[answer.student.team.division][answer.student.subject1])

    def subject2_question_grader(self, question, answer):
        """Grade an individual question."""

        return (question.weight * (answer.value or 0) *
                self.individual_bonus[answer.student.team.division][answer.student.subject2])

    def guts_question_grader(self, question: g.Question, answer: g.Answer):
        """Grade a guts question."""

        value = 0
        if question.type == g.QUESTION_TYPES["correct"]:
            value = answer.value
        elif question.type == g.QUESTION_TYPES["estimation"]:
            e = answer.value
            a = question.answer
            if a is None:
                value = 0
            elif question.number == 26:
                max_below = g.Answer.objects.filter(
                    value__isnull=False, value__lte=e).exclude(answer).order_by("value").first()
                value = min(12, e - max_below)
            elif question.number == 27:
                value = 12 * 2 ** (-abs(e-a)/60)
            elif question.number == 28:
                value = 0 if e <= 0 else 12 * (16 * math.log10(max(e/a, a/e)) + 1) ** (-0.5)
            elif question.number == 29:
                value = 0 if e <= 0 else 12 * min(e/a, a/e)
            elif question.number == 30:
                value = 0 if e <= 0 else max(0, 12 - 4 * math.log10(max(e/a, a/e)))
        return value * question.weight

    def team_z_round_grader(self, round: g.Round):
        """General team round grader based on Z score."""

        raw_scores = self.grade_round(round)
        for division in raw_scores:
            data = list(map(lambda team: raw_scores[division][team], raw_scores[division]))
            mean = statistics.mean(data)
            dev = statistics.stdev(data, mean)
            for team in raw_scores[division]:
                raw_scores[division][team] = 0 if dev == 0 else (raw_scores[division][team] - mean) / dev
        return raw_scores

    def team_round_grader(self, round: g.Round):
        """Grader for the team round."""

        return self.team_z_round_grader(round)

    # Cached for use in live grading
    @cached(cache, "guts_scores")
    def guts_round_grader(self, round: g.Round):
        """Grader for the guts round."""

        return self.team_z_round_grader(round)

    @cached(cache, "individual_scores")
    def calculate_individual_scores(self):
        """Custom function that groups both subject rounds together."""

        subject1 = self.competition.rounds.filter(ref="subject1").first()
        subject2 = self.competition.rounds.filter(ref="subject2").first()
        self._calculate_individual_modifiers(subject1, subject2)
        raw_scores1 = self.grade_round(subject1)
        raw_scores2 = self.grade_round(subject2)
        split_scores = ChillDictionary()
        subject_scores = ChillDictionary()

        # This ignores students who received answers for one test but not another
        for division in set(raw_scores1.keys()) & set(raw_scores2.keys()):
            for student in set(raw_scores2[division].keys()) & set(raw_scores2[division].keys()):
                score1 = raw_scores1[division][student]
                score2 = raw_scores2[division][student]
                split_scores[division][student] = {student.subject1: score1, student.subject2: score2}
                subject_scores[division].set(student.subject1, []).append(score1)
                subject_scores[division].set(student.subject2, []).append(score2)

        powers = ChillDictionary()
        for division in subject_scores:
            for subject in subject_scores[division]:
                powers[division][subject] = self._calculate_individual_exponent(subject_scores[division][subject])

        final_scores = ChillDictionary()
        for division in split_scores:
            for student in split_scores[division]:
                score = 0
                for subject in split_scores[division][student]:
                    score += pow(split_scores[division][student][subject], powers[division][subject])
                final_scores[division][student] = score

        return final_scores.dict()

    @cached(cache, "team_individual_scores")
    def calculate_team_individual_scores(self):
        """Custom function that combines team and guts scores."""

        raw_scores = self.calculate_individual_scores(cache=True)
        final_scores = ChillDictionary()
        for team in f.Team.current():
            score = 0
            count = 0
            for student in team:
                score += raw_scores[team.division][student]
                count += 1
            final_scores[team.division][team] = score / count
        return final_scores.dict()

    @cached(cache, "team_overall_scores")
    def calculate_team_scores(self):
        """Calculate the team scores."""

        team_round = self.competition.rounds.filter(ref=TEAM).first()
        guts_round = self.competition.rounds.filter(ref=GUTS).first()
        individual_scores = self.calculate_team_individual_scores(cache=True)
        team_round_scores = self.team_round_grader(team_round)
        guts_round_scores = self.guts_round_grader(guts_round)
        final_scores = ChillDictionary()
        for team in f.Team.current():
            score = 0.4*individual_scores[team] + 0.3*team_round_scores[team] + 0.3*guts_round_scores[team]
            final_scores[team.division][team] = score
        return final_scores.dict()

    def grade_competition(self, competition):
        """Grade the entire competition."""

        pass
