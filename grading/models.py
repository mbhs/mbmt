from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save

import frontend.models
from frontend.models import Competition


_ROUND_GROUPINGS = (
    (0, "individual"),
    (1, "team"))
ROUND_GROUPINGS = {
    0: "individual", 1: "team",
    "individual": 0, "team": 1}

_QUESTION_TYPES = (
    (0, "correct"),
    (1, "estimation"))
QUESTION_TYPES = {
    0: "correct", 1: "estimation",
    "correct": 0, "estimation": 1}


@receiver(post_save, sender=Competition)
def save_rounds(sender: type, instance: Competition, **options):
    """Save rounds when a competition is saved"""

    for round in instance.rounds:
        round.save()


class Round(models.Model):
    """A single competition round."""

    id = models.CharField(max_length=12, primary_key=True)
    name = models.CharField(max_length=64)
    competition = models.ForeignKey(Competition, related_name="rounds")
    grouping = models.IntegerField(choices=_ROUND_GROUPINGS)

    def __repr__(self):
        """Represent the round as a string."""

        return "Round[{}]".format(self.name)

    @staticmethod
    def new(competition: Competition, iid: str, save: bool=True, **options):
        """Initialize the new round as part of the competition."""

        round = Round(competition=competition, id=iid, **options)
        if save:
            round.save()
        return round


@receiver(post_save, sender=Round)
def save_rounds(sender: type, instance: Round, **options):
    """Save rounds when a competition is saved"""

    for question in instance.questions:
        question.save()


class Question(models.Model):
    """A question container model."""

    round = models.ForeignKey(Round, related_name="questions")
    order = models.IntegerField()
    label = models.CharField(max_length=32)
    type = models.IntegerField(choices=_QUESTION_TYPES)
    weight = models.FloatField(default=1.0)
    answer = models.FloatField(blank=True, null=True)

    @staticmethod
    def new(round: Round, iid: str, save: bool=True, **options):
        """Create a new question within the round."""

        question = Question(round=round, id=iid, **options)
        if save:
            question.save()
        return question


class Answer(models.Model):
    """An answer to a question."""

    question = models.ForeignKey(Question, related_name="answers")
    student = models.ForeignKey(frontend.models.Student, related_name="answers", null=True, blank=True)
    team = models.ForeignKey(frontend.models.Team, related_name="answers", null=True, blank=True)
    value = models.FloatField(null=True, blank=True)
