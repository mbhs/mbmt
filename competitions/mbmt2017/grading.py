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
from grading.grading import CompetitionGrader, ChillDictionary, cached, cache_get, cache_set
from grading.models import CORRECT, ESTIMATION


SUBJECT1 = "subject1"
SUBJECT2 = "subject2"
GUTS = "guts"
TEAM = "team"


def normalize(array, n):
    """Divide array values by n."""

    return list(map(lambda x: x/n, array))


class Grader(CompetitionGrader):
    """Grader specific to MBMT 2017."""

    LAMBDA = 0.52

    cache = {}

    def __init__(self, competition: g.Competition):
        """Initialize the MBMT 2017 grader."""

        super().__init__(competition)
        self.individual_bonus = {}
        self.individual_powers = {}

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

        factors = ChillDictionary({division: ChillDictionary() for division in f.DIVISIONS_MAP})
        for i, round in enumerate((round1, round2)):
            for question in round.questions.all():
                for answer in g.Answer.objects.filter(question=question).all():

                    # Ignore absent students
                    if not answer.student.attending:
                        continue

                    # Ignores people whose grading view is not opened
                    division = answer.student.team.division
                    subject = answer.student.subject1 if i == 0 else answer.student.subject2

                    # Set atomic factor to correct and total values
                    if question not in factors[division][subject]:
                        factors[division][subject][question] = [0, 0]  # Correct, total
                    factors[division][subject][question][0] += answer.value or 0
                    factors[division][subject][question][1] += 1

        for division in factors:
            self.individual_bonus[division] = {}
            for subject in factors[division]:
                self.individual_bonus[division][subject] = {}
                for question in factors[division][subject]:
                    correct, total = factors[division][subject][question]
                    self.individual_bonus[division][subject][question.id] = (
                        self.LAMBDA * math.log(total / (correct+1)))

    def _power_average_partial(self, scores):
        """Return a partial that averages scores raised to a power."""

        def power_average(d):
            return 0.375 - 1.0/len(scores) * sum(pow(score, d) for score in scores)
        return power_average

    def _calculate_individual_exponent(self, scores):
        """Determines the exponent for an individual subject test."""

        return scipy.optimize.newton(self._power_average_partial(scores), 1, tol=0.0001, maxiter=1000)

    def subject1_question_grader(self, question, answer):
        """Grade an individual question."""

        return (question.weight * (answer.value or 0) * (1 +
                self.individual_bonus[answer.student.team.division][answer.student.subject1][question.id]))

    def subject2_question_grader(self, question, answer):
        """Grade an individual question."""

        return (question.weight * (answer.value or 0) * (1 +
                self.individual_bonus[answer.student.team.division][answer.student.subject2][question.id]))

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

    def z_score(self, raw_scores):
        """General team round grader based on Z score."""

        scores = ChillDictionary()
        for division in raw_scores:
            data = list(map(lambda team: raw_scores[division][team], raw_scores[division]))
            mean = statistics.mean(data)
            dev = statistics.stdev(data, mean)
            for team in raw_scores[division]:
                scores[division][team] = 0 if dev == 0 else (raw_scores[division][team] - mean) / dev
        return scores.dict()

    @cached(cache, "team_scores")
    def team_round_grader(self, round: g.Round):
        """Grader for the team round."""

        raw_scores = self.grade_round(round)
        self.cache_set("raw_team_scores", raw_scores)
        return self.z_score(raw_scores)

    # Cached for use in live grading
    @cached(cache, "guts_scores")
    def guts_round_grader(self, round: g.Round):
        """Grader for the guts round."""

        raw_scores = self.grade_round(round)
        self.cache_set("raw_guts_scores", raw_scores)
        return self.z_score(raw_scores)

    @cached(cache, "raw_guts_score")
    def guts_live_round_scores(self):
        """Guts live round."""

        round = self.competition.rounds.filter(ref="guts").first()
        return self.grade_round(round)

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
        for division in f.DIVISIONS_MAP:

            # Set up dictionary so no missing keys
            subject_scores[division] = ChillDictionary()
            for subject in f.SUBJECT_CHOICES_MAP:
                subject_scores[division][subject] = ChillDictionary()

            split_scores[division] = ChillDictionary()
            for student in set(raw_scores2[division].keys()) & set(raw_scores2[division].keys()):

                # Skip students not attending
                if not student.attending:
                    continue

                score1 = raw_scores1[division][student]
                score2 = raw_scores2[division][student]
                split_scores[division][student] = {student.subject1: score1, student.subject2: score2}
                subject_scores[division][student.subject1][student] = score1
                subject_scores[division][student.subject2][student] = score2

        self.cache_set("subject_scores", subject_scores.dict())

        powers = ChillDictionary()
        max_scores = ChillDictionary()
        for division in subject_scores:
            for subject in subject_scores[division]:
                # scores = list(filter(lambda x: x > 0, subject_scores[division][subject].values()))
                scores = list(subject_scores[division][subject].values())
                high = 0 if not scores else max(scores)
                max_scores[division][subject] = high

                # Doesn't work for fewer than 3 scores
                if len(scores) >= 3:
                    powers[division][subject] = self._calculate_individual_exponent(normalize(scores, high))

                # Doesn't work for fewer than 3 scores
                else:
                    powers[division][subject] = 0
        self.individual_powers = powers.dict()

        raw_scores = ChillDictionary()
        final_scores = ChillDictionary()
        for division in split_scores:
            final_scores[division] = ChillDictionary()
            for student in split_scores[division]:
                score = 0
                raw_score = []
                for subject in split_scores[division][student]:
                    if split_scores[division][student][subject] != 0:
                        score += pow(
                            split_scores[division][student][subject] / max_scores[division][subject],
                            powers[division][subject])
                        raw_score.append(split_scores[division][student][subject])
                raw_scores[division][student] = score
                final_scores[division][student] = score

        self.cache_set("raw_individual_scores", raw_scores.dict())

        return final_scores.dict()

    @cached(cache, "team_individual_scores")
    def calculate_team_individual_scores(self):
        """Custom function that combines team and guts scores."""

        raw_scores = self.calculate_individual_scores(use_cache=True)
        final_scores = ChillDictionary()
        for team in f.Team.current():
            score = 0
            count = 0
            for student in team.students.all():
                if student.attending and team.division in raw_scores and student in raw_scores[team.division]:
                    score += raw_scores[team.division][student]
                    count += 1
            final_scores[team.division][team] = 0 if count == 0 else score / count
        return final_scores.dict()

    @cached(cache, "team_overall_scores")
    def calculate_team_scores(self, use_cache=True):
        """Calculate the team scores."""

        team_round = self.competition.rounds.filter(ref=TEAM).first()
        guts_round = self.competition.rounds.filter(ref=GUTS).first()
        individual_scores = self.calculate_team_individual_scores(use_cache=use_cache)
        team_round_scores = self.team_round_grader(team_round, use_cache=use_cache)
        guts_round_scores = self.guts_round_grader(guts_round, use_cache=use_cache)

        final_scores = ChillDictionary()
        for division in f.DIVISIONS_MAP:
            for team in f.Team.current():
                if team in individual_scores[division] and team in team_round_scores[division] and team in guts_round_scores[division]:
                    score = (
                        0.4*individual_scores[division][team] +
                        0.3*team_round_scores[division][team] +
                        0.3*guts_round_scores[division][team])
                    final_scores[team.division][team] = score
        return final_scores.dict()

    def grade_competition(self, competition):
        """Grade the entire competition."""

        pass
