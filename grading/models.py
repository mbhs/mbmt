from django.db import models
# from django.dispatch import receiver
# from django.db.models.signals import post_save

from home.models import Competition
from coaches.models import Team, Student

_ROUND_GROUPINGS = (
    (0, "individual"),
    (1, "team"))
ROUND_GROUPINGS = {
    0: "individual", 1: "team",
    "individual": 0, "team": 1}
INDIVIDUAL = 0
TEAM = 1

_QUESTION_TYPES = (
    (0, "correct"),
    (1, "estimation"))
QUESTION_TYPES = {
    0: "correct", 1: "estimation",
    "correct": 0, "estimation": 1}
CORRECT = 0
ESTIMATION = 1


class Round(models.Model):
    """A single competition round."""

    ref = models.CharField(max_length=12)
    name = models.CharField(max_length=64)
    competition = models.ForeignKey(Competition, related_name="rounds")
    grouping = models.IntegerField(choices=_ROUND_GROUPINGS)

    # TODO: consider having general polymorphic rounds
    # Have single or multiple tests that can be taken by choice
    # Somehow link to student and form for actual test PDF

    def __repr__(self):
        """Represent the round as a string."""

        return "Round[{}]".format(self.name)

    @staticmethod
    def new(competition: Competition, ref: str, save: bool=True, **options):
        """Initialize the new round as part of the competition."""

        round = Round(competition=competition, ref=ref, **options)
        if save:
            round.save()
        return round


# Unnecessary at the moment
#
# @receiver(post_save, sender=Round)
# def save_rounds(sender: type, instance: Round, **options):
#     """Save rounds when a competition is saved"""
#
#     for question in instance.questions.all():
#         question.save()


class Question(models.Model):
    """A question container model."""

    round = models.ForeignKey(Round, related_name="questions")
    number = models.IntegerField()
    label = models.CharField(max_length=32)
    type = models.IntegerField(choices=_QUESTION_TYPES)
    weight = models.FloatField(default=1.0)
    answer = models.FloatField(blank=True, null=True)

    # TODO: Make sure this is the optimal information for a question
    # Consider having a statistics utility for the question model that
    # returns correct, incorrect, and skipped counts.

    def __repr__(self):
        """Represent the question as a string."""

        return "Question[#{}]".format(self.number)

    @staticmethod
    def new(round: Round, number: int, save: bool=True, **options):
        """Create a new question within the round."""

        question = Question(round=round, number=number, **options)
        if save:
            question.save()
        return question

    # Automated question grading
    # This feature may eventually be implemented for summer competitions
    # or other MBMT events. If we generalize our platform to science
    # bowl, it could be the case that answer would also have to support
    # multiple choice, in which case storing values rather than true or
    # false will be more important


class Answer(models.Model):
    """An answer to a question."""

    question = models.ForeignKey(Question, related_name="answers")
    student = models.ForeignKey(Student, related_name="answers", null=True, blank=True)
    team = models.ForeignKey(Team, related_name="answers", null=True, blank=True)
    value = models.FloatField(null=True, blank=True)

    # TODO: answers have to be queried for statistics, so either the
    # statistics wrapper make such queries or the queries will be
    # defined under the answer model.
