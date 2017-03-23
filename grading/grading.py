"""Framework for defining custom grading schemes for competitions.

The competition grader is intended to be sub-classed in the custom
file structure under the competitions directory, from which it will be
dynamically imported into into the view that handles grading.

competitions/
  my_competition/
    competition.json
    grading.py

The competition grader resolution order is first to grade a question
provided its answer, and second to grade rounds based on the result of
the values returned.
"""

from django.db.models import Q

import frontend.models
from . import models


ROUND = "round"
QUESTION = "question"


def cached(cache: dict, name: object):
    """Decorator that caches the return of a function.

    Intended as a quick way to save on computation. Since decorators
    within class declarations cannot reference the class, the cache
    container must be passed manually.

    In addition to caching the output every time the function is
    called, the decorator adds the `cached` keyword argument to the
    function declaration. If the cached flag is set to true, the
    output from the last call to the function, if available, is
    returned. Otherwise, the function is called again.
    """

    def decorator(function):
        def wrapper(*args, cached: bool=True, **kwargs):
            if cached and name in cache:
                return cache[name]
            result = function(*args, **kwargs)
            cache[name] = result
            return result
        return wrapper
    return decorator


class ChillDictionary(dict):
    """Dictionary that sets empty keys to chill dictionaries."""

    def __missing__(self, key):
        """Called when a missing key is invoked."""

        new = ChillDictionary()
        self[key] = new
        return new


class CompetitionGrader:
    """Base class for a competition grader.

    The competition grader should be instantiated by the corresponding
    competition object. The functionality for this is already provided
    in the model declaration.
    """

    def __init__(self, competition: models.Competition):
        """Initialize the competition grader."""

        self.competition = competition
        self.question_graders = {}
        self.round_graders = {}

    ####################
    # Question graders #
    ####################

    def default_question_grader(self, question: models.Question, answer: models.Answer):
        """Default action for grading a question."""

        return question.weight * (answer.value or 0)

    def default_round_grader(self, round: models.Round):
        """Default action for grading a round."""

        if round.grouping == models.ROUND_GROUPINGS["individual"]:
            model = frontend.models.Student
            group = "student"
        elif round.grouping == models.ROUND_GROUPINGS["team"]:
            model = frontend.models.Team
            group = "team"
        else:
            return None

        # Iterate through teams or students
        scores = ChillDictionary()
        for thing in model.current():
            score = 0
            for question in round.questions.all():
                answer = models.Answer.objects.filter(**{group: thing}, question=question).first()
                if answer:
                    result = self.get_question_grader(question)(question, answer)
                    score += result or 0

            # Separate by division
            division = None
            if group == "student":
                division = thing.team.division
            elif group == "team":
                division = thing.division

            # Save score
            scores[division][thing] = score

        return scores

    #######################
    # Grader registration #
    #######################

    def register_question_grader(self, query: Q, function):
        """Register a question grading function to a set of questions."""

        for question in models.Question.objects.filter(query, round__competition=self.competition).all():
            self.question_graders[question.id] = function

    def register_round_grader(self, query: Q, function):
        """Register a round grading function to a set of questions."""

        for round in models.Round.objects.filter(query, competition=self.competition).all():
            self.round_graders[round.id] = function

    #####################
    # Grader resolution #
    #####################

    def get_question_grader(self, question: models.Question):
        """Get the registered question grader by the question model."""

        return self.question_graders.get(question.id, self.default_question_grader)

    def get_round_grader(self, round: models.Round):
        """Get the registered round grader by the round model."""

        return self.round_graders.get(round.id, self.default_round_grader)

    ##################
    # Actual graders #
    ##################

    def grade_round(self, round: models.Round):
        """Grade a round."""

        return self.get_round_grader(round)(round)

    def grade_competition(self):
        """Grade a competition."""

        results = {}
        for round in self.competition.rounds.all():
            results[round.ref] = self.grade_round(round)
        return results
