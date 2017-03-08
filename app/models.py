"""Models for the competition and response."""

from django.db import models
from django.contrib.auth.models import User


_SUBJECT_CHOICES = (
    ("al", "Algebra"),
    ("nt", "Number Theory"),
    ("ge", "Geometry"),
    ("cp", "Counting and Probability"))

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

_DIVISIONS = (
    (1, "Pascal"),
    (2, "Ramanujan"))
DIVISIONS = {
    1: "Pascal", 2: "Ramanujan"}

_SHIRT_SIZES = (
    (0, "Default"),
    (1, "Adult Small"),
    (2, "Adult Medium"),
    (3, "Adult Large"),
    (4, "Adult Extra Large"))
SHIRT_SIZES = _SHIRT_SIZES
#SHIRT_SIZES = list(map(lambda x: x[1], _SHIRT_SIZES))


class School(models.Model):
    """A simple school model that is represented by a teacher."""

    name = models.CharField(max_length=256)
    user = models.OneToOneField(User, related_name="school")

    def __str__(self):
        """Represent the school as a string."""

        return "School[{}]".format(self.name)


class Team(models.Model):
    """Represents a team of students competing in the competition."""

    name = models.CharField(max_length=256)
    school = models.ForeignKey(School, related_name="teams")
    division = models.IntegerField(choices=_DIVISIONS)

    def __str__(self):
        return "Team[{}]".format(self.name)


class Student(models.Model):
    """A student participating in the competition."""

    name = models.CharField(max_length=256, blank=True)
    subject1 = models.CharField(max_length=2, blank=True, choices=_SUBJECT_CHOICES, verbose_name="Subject 1")
    subject2 = models.CharField(max_length=2, blank=True, choices=_SUBJECT_CHOICES, verbose_name="Subject 2")
    team = models.ForeignKey(Team, related_name="students")
    size = models.IntegerField(choices=_SHIRT_SIZES, default=0)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return "Student[{}]".format(self.name)


class Competition(models.Model):
    """An competition question container."""

    id = models.CharField(max_length=12, primary_key=True)
    name = models.CharField(max_length=128)
    year = models.IntegerField()
    active = models.BooleanField(default=False)

    def __repr__(self):
        """Represent the competition as a string."""

        return "Competition[{}]".format(self.name)

    @staticmethod
    def get_active():
        """Get the active competition."""

        return Competition.objects.filter(active=True).first()

    def save_all(self):
        """Save self and all rounds and questions."""

        self.save()
        for round in self.rounds:
            round.save_all()


class Round(models.Model):
    """A single competition round."""

    id = models.CharField(max_length=12, primary_key=True)
    name = models.CharField(max_length=64)
    competition = models.ForeignKey(Competition, related_name="rounds")
    grouping = models.IntegerField(choices=_ROUND_GROUPINGS)

    @staticmethod
    def new(competition, id, name, grouping):
        """Make a new round."""

        round = Round(competition=competition, id=id, name=name, grouping=grouping)
        round.save()
        return round

    def __repr__(self):
        """Represent the round as a string."""

        return "Round[{}]".format(self.name)

    def save_all(self):
        """Save self and all questions."""

        self.save()
        for question in self.questions:
            question.save()


class Question(models.Model):
    """A question container model."""

    round = models.ForeignKey(Round, related_name="questions")
    order = models.IntegerField()
    label = models.CharField(max_length=32)
    type = models.IntegerField(choices=_QUESTION_TYPES)

    @staticmethod
    def new(round, order, label, type):
        """Instantiate a new question."""

        question = Question(round=round, order=order, label=label, type=type)
        question.save()


class Answer(models.Model):
    """An answer to a question."""

    question = models.ForeignKey(Question, related_name="answers")
    student = models.ForeignKey(Student, related_name="answers", null=True, blank=True)
    team = models.ForeignKey(Team, related_name="answers", null=True, blank=True)
    value = models.FloatField(null=True, blank=True)
