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

import time

import coaches.models
from . import models


ROUND = "round"
QUESTION = "question"


class CachedGrade:
    """Meta container object that stores cached results and timing."""

    def __init__(self, result, when=None):
        """Initialize a cache object."""

        self.result = result
        self.time = when or time.time()


def cache_set(cache, name, result):
    """Set an item in the cache manually."""

    cache[name] = CachedGrade(result, time.time())


def cache_get(cache, name):
    """Get an item from the cache."""

    item = cache.get(name)
    return None if item is None else item.result


def cached(cache: dict, name: object):
    """Decorator that caches the return of a function.

    Intended as a quick way to save on computation. Since decorators
    within class declarations cannot reference the class, the cache
    container must be passed manually.

    In addition to caching the output every time the function is
    called, the decorator adds the `use_cache` keyword argument to the
    function declaration. If the `use_cache` flag is set to true, the
    output from the last call to the function, if available, is
    returned. Otherwise, the function is called again. In order to
    provide a global caching mechanism, `use_cache_before` can be set
    instead, which uses the cached value until a number of seconds
    since the last recalculation.
    """

    def decorator(function):
        def wrapper(*args, use_cache: bool=True, use_cache_before: int=0, **kwargs):

            # Use cache time before normal cache
            if use_cache_before > 0 and name in cache:
                if cache[name].time >= time.time() - use_cache_before:
                    return cache_get(cache, name)

            # Then check cache normally, only if use_cache_before is 0
            elif use_cache and name in cache:
                return cache_get(cache, name)

            if "use_cache" in function.__code__.co_varnames:
                kwargs["use_cache"] = use_cache

            result = function(*args, **kwargs)
            cache_set(cache, name, result)
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

    def set(self, key, default):
        """Similar to get, except sets the internal key to the default."""

        if key in self:
            return self[key]
        self[key] = default
        return default

    def dict(self):
        """Cast to a dictionary."""

        out = dict()
        for key in self:
            if isinstance(self[key], ChillDictionary):
                out[key] = self[key].dict()
            else:
                out[key] = self[key]
        return out


class CompetitionGrader:
    """Base class for a competition grader.

    The competition grader should be instantiated by the corresponding
    competition object. The functionality for this is already provided
    in the model declaration.
    """

    cache = {}

    def __init__(self, competition: models.Competition):
        """Initialize the competition grader."""

        self.competition = competition
        self.question_graders = {}
        self.round_graders = {}

    ################
    # Cache access #
    ################

    def cache_get(self, name):
        """Get an item from the cache."""

        return cache_get(self.cache, name)

    def cache_set(self, name, result):
        """Set an item in the cache."""

        cache_set(self.cache, name, result)

    ####################
    # Question graders #
    ####################

    def default_question_grader(self, question: models.Question, answer: models.Answer):
        """Default action for grading a question."""

        return question.weight * (answer.value or 0)

    def default_round_grader(self, round: models.Round):
        """Default action for grading a round."""

        if round.grouping == models.ROUND_GROUPINGS["individual"]:
            model = coaches.models.Student
            group = "student"
        elif round.grouping == models.ROUND_GROUPINGS["team"]:
            model = coaches.models.Team
            group = "team"
        else:
            return None

        # Iterate through teams or students
        scores = ChillDictionary()
        for division in coaches.models.DIVISIONS_MAP:
            scores[division] = ChillDictionary()

        for thing in model.current():

            if group == "student" and not thing.attending:
                continue

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


def prepare_individual_scores(scores):
    """Prepare the scores from a question score calculation."""

    divisions = []
    for division in sorted(scores.keys()):
        division_name = coaches.models.DIVISIONS_MAP[division]
        things = []
        for thing in scores[division]:
            things.append((thing.name, scores[division][thing]))
        things.sort(key=lambda x: x[1], reverse=True)
        divisions.append((division_name, things))
    return divisions


def prepare_subject_scores(scores):
    """Prepare scores recursively."""

    divisions = []
    for division in sorted(scores.keys()):
        division_name = coaches.models.DIVISIONS_MAP[division]
        subjects = []
        for subject in scores[division]:
            students = []
            for student in scores[division][subject]:
                students.append((student.name, scores[division][subject][student]))
            students.sort(key=lambda x: x[1], reverse=True)
            subjects.append((coaches.models.SUBJECTS_MAP[subject], students))
        subjects.sort(key=lambda x: x[0])
        divisions.append((division_name, subjects))
    return divisions


def prepare_composite_team_scores(guts_scores, guts_z, team_scores, team_z,
                                  team_individual_scores, overall_scores):
    """Prepare team scores for scoreboard."""

    divisions = []
    for division in sorted(overall_scores.keys()):
        division_name = coaches.models.DIVISIONS_MAP[division]
        teams = []
        for team in overall_scores[division]:
            teams.append((
                team.name,
                guts_scores[division].get(team, 0),
                guts_z[division].get(team, 0),
                team_scores[division].get(team, 0),
                team_z[division].get(team, 0),
                team_individual_scores[division].get(team, 0),
                overall_scores[division].get(team, 0)))
        teams.sort(key=lambda x: x[-1], reverse=True)
        divisions.append((division_name, teams))
    return divisions


def prepare_school_team_scores(school, guts_scores, team_scores, team_individual_scores, overall_scores):
    """Prepare scores for sponsor scoreboard."""

    divisions = []
    for division in sorted(overall_scores.keys()):
        division_name = coaches.models.DIVISIONS_MAP[division]
        teams = []
        for team in overall_scores[division]:
            if team.school != school:
                continue
            teams.append((
                team.name,
                guts_scores[division].get(team, 0),
                team_scores[division].get(team, 0),
                team_individual_scores[division].get(team, 0),
                overall_scores[division].get(team, 0)))
        teams.sort(key=lambda x: x[-1], reverse=True)
        divisions.append((division_name, teams))
    return divisions


def prepare_school_individual_scores(school, scores):
    """Prepare individual scores for sponsor scoreboard."""

    divisions = []
    for division in scores:
        students = {}
        for i, subject in enumerate(sorted(coaches.models.SUBJECTS_MAP.keys())):
            for student in scores[division][subject]:
                if student.team.school != school:
                    continue
                if student not in students:
                    students[student] = [None, None, None, None]
                students[student][i] = scores[division][subject][student]
        students = list(map(lambda x: (x[0].name, x[1]), students.items()))
        students.sort(key=lambda x: x[0])
        divisions.append((coaches.models.DIVISIONS_MAP[division], students))
    return divisions
