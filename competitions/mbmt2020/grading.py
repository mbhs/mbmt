"""The official MBMT 2020 grading algorithm.
The following file is intended for use as a modular plugin that
implements various grading functions for the MBMT website. In order
grading functions must be registered to either a round ID and
optionally a question ID.

No change from 2018 as of 1/10/20 - Matthew
"""


from django.db.models import Q

import math
import itertools

import scipy.optimize

import grading.models as g
import coaches.models as c
from grading.grading import CompetitionGrader, ChillDictionary, cached
from grading.models import CORRECT, ESTIMATION


SUBJECT1 = "subject1"
SUBJECT2 = "subject2"
GUTS = "guts"
TEAM = "team"


def multiply(array, l):
    """Multiply array values by l."""

    return dict(map(lambda t: (t[0], dict(map(lambda u: (u[0], u[1]*l), t[1].items()))), array.items()))


class Grader(CompetitionGrader):
    """Grader specific to MBMT 2020."""
    cache = {}

    def __init__(self, competition: g.Competition):
        super().__init__(competition)
        self.individual_weight = {}
        self.individual_maxes = {}

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

        self.individual_weight = {}
        self.individual_maxes = ChillDictionary()

        factors = ChillDictionary({division: ChillDictionary() for division in c.DIVISIONS_MAP})
        for i, round in enumerate((round1, round2)):
            for question in round.questions.all():
                for answer in g.Answer.objects.filter(question=question).all():

                    # Ignore absent students
                    if not answer.student.attending:
                        continue

                    # Ignores people2017 whose grading view is not opened
                    division = answer.student.team.division
                    subject = answer.student.subject1 if i == 0 else answer.student.subject2

                    # Set atomic factor to correct and total values
                    if question.number not in factors[division][subject]:
                        factors[division][subject][question.number] = [0, 0]  # Correct, total
                    factors[division][subject][question.number][0] += answer.value or 0
                    factors[division][subject][question.number][1] += 1

        for division in factors:
            self.individual_weight[division] = {}
            for subject in factors[division]:
                self.individual_weight[division][subject] = {}
                for question in factors[division][subject]:
                    correct, total = factors[division][subject][question]
                    weight = 2 + math.log((total+2) / (correct+2))
                    self.individual_weight[division][subject][question] = weight
                    self.individual_maxes[division][subject] = self.individual_maxes[division].get(subject, 0) + weight

    def subject1_question_grader(self, question, answer):
        """Grade an individual question."""

        return question.weight * (answer.value or 0) * self.individual_weight[answer.student.team.division][answer.student.subject1][question.number]

    def subject2_question_grader(self, question, answer):
        """Grade an individual question."""

        return question.weight * (answer.value or 0) * self.individual_weight[answer.student.team.division][answer.student.subject2][question.number]

    def guts_question_grader(self, question: g.Question, answer: g.Answer):
        """Grade a guts question."""

        value = 0
        if question.type == g.QUESTION_TYPES["correct"]:
            value = answer.value
        elif question.type == g.QUESTION_TYPES["estimation"]:
            e = answer.value
            a = question.answer
            if e is None:
                value = 0
            #change this every year to modify the estimation formulas
            elif question.number == 26:
                value = 0 if e <= 0 else max(0, 12-abs(a-e)/5) / 12
            elif question.number == 27:
                value = 0 if e <= 0 else max(0, 12-100*abs(a-e)) / 12
            elif question.number == 28:
                value = 0 if e <= 0 else max(0, 12-5*abs(a-e)) / 12
            elif question.number == 29:
                value = 0 if e <= 0 else 12*max(0, 1-3*abs(a-e)/a) / 12
            elif question.number == 30:
                value = 0 if e <= 0 else max(0, 12-abs(a-e)/2000) / 12
        return value * question.weight

    @cached(cache, "team_scores")
    def team_round_grader(self, round: g.Round):
        """Grader for the team round."""

        raw_scores = self.grade_round(round)
        self.cache_set("raw_team_scores", raw_scores)

        maxscore = 0
        for q in round.questions.all():
            maxscore += q.weight
        return multiply(raw_scores, 1/maxscore)


    # Cached for use in live grading
    @cached(cache, "guts_scores")
    def guts_round_grader(self, round: g.Round):
        """Grader for the guts round."""

        raw_scores = self.grade_round(round)
        self.cache_set("raw_guts_scores", raw_scores)

        maxscore = 0
        for q in round.questions.all():
            maxscore += q.weight
        return multiply(raw_scores, 1/maxscore)

    @cached(cache, "raw_guts_score")
    def guts_live_round_scores(self):
        """Guts live round."""

        round = self.competition.rounds.filter(ref="guts").first()
        return self.grade_round(round)

    def logistic_regularization(self, categories, observations, weights=None):
        if not weights:
            weights = {c:1 for c in categories}
        d = len(categories)
        def transform(s, a):
            return s/(s+math.e**a*(1-s))
        def loss(x):
            # Calc exponents
            factors = {}
            for i in range(d-1):
                factors[categories[i]] = x[i]
            factors[categories[d-1]] = -sum([weights[categories[i]]*x[i]for i in range(d-1)])/weights[categories[d-1]]

            L = 0

            for obs in observations.values():
                for c1, c2 in itertools.combinations(obs.keys(), 2):
                    L += weights[c1] * weights[c2] * obs[c1]*obs[c2]*(transform(obs[c1], factors[c1]) - transform(obs[c2], factors[c2]))**2
            return L
        results = scipy.optimize.least_squares(loss, [0]*(d-1), ftol=1e-12)
        x = results.x
        factors = {}
        for i in range(d-1):
            factors[categories[i]] = x[i]
        factors[categories[d-1]] = -sum([weights[categories[i]]*x[i]for i in range(d-1)])/weights[categories[d-1]]
        print(factors)

        normalized = {}
        for inst, obs in observations.items():
            normalized[inst] = sum([weights[c] * transform(obs.get(c, 0), factors[c]) for c in categories])
        return normalized

    def logistic_regularization_mdiv(self, categories, observations, weights=None):
        normalized = {}
        for k, v in observations.items():
            normalized[k] = self.logistic_regularization(categories, v, weights)
        return normalized

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
        for division in c.DIVISIONS_MAP:

            # Set up dictionary so no missing keys
            subject_scores[division] = ChillDictionary()
            for subject in c.SUBJECTS_MAP:
                subject_scores[division][subject] = ChillDictionary()

            split_scores[division] = ChillDictionary()
            for student in set(raw_scores1[division].keys()) & set(raw_scores2[division].keys()):

                # Skip students not attending
                if not student.attending:
                    continue

                score1 = raw_scores1[division][student]
                score2 = raw_scores2[division][student]
                split_scores[division][student] = {student.subject1: score1 / self.individual_maxes[division][student.subject1],
                                                   student.subject2: score2 / self.individual_maxes[division][student.subject2]}
                subject_scores[division][student.subject1][student] = score1
                subject_scores[division][student.subject2][student] = score2

        self.cache_set("subject_scores", subject_scores.dict())

        return self.logistic_regularization_mdiv(list(c.SUBJECTS_MAP.keys()), split_scores)

    @cached(cache, "team_individual_scores")
    def calculate_team_individual_scores(self):
        """Custom function that combines team and guts scores."""

        raw_scores = self.calculate_individual_scores(use_cache=True)
        final_scores = ChillDictionary()
        for team in c.Team.current():
            score = 0
            count = 0
            for student in team.students.all():
                if student.attending and team.division in raw_scores and student in raw_scores[team.division]:
                    score += raw_scores[team.division][student]
            final_scores[team.division][team] = score / 10
        return final_scores.dict()

    @cached(cache, "team_overall_scores")
    def calculate_team_scores(self, use_cache=True):
        """Calculate the team scores."""

        team_round = self.competition.rounds.filter(ref=TEAM).first()
        guts_round = self.competition.rounds.filter(ref=GUTS).first()
        individual_scores = self.calculate_team_individual_scores(use_cache=use_cache)
        team_round_scores = self.team_round_grader(team_round, use_cache=use_cache)
        guts_round_scores = self.guts_round_grader(guts_round, use_cache=use_cache)

        raw_teamscores = ChillDictionary()

        for team in c.Team.current():
            raw_teamscores[team.division][team]["indiv"] = individual_scores[team.division][team]
            raw_teamscores[team.division][team]["team"] = team_round_scores[team.division][team]
            raw_teamscores[team.division][team]["guts"] = guts_round_scores[team.division][team]

        return self.logistic_regularization_mdiv(["indiv", "team", "guts"], raw_teamscores, {"indiv": 50, "team": 25, "guts": 25})

    def grade_competition(self):
        """Grade the entire competition."""

        pass
