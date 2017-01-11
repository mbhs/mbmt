"""Models for the competition and response."""

from django.db import models
from django.contrib.auth.models import User


SUBJECT_CHOICES = (
    ("al", "Algebra"),
    ("nu", "Number Theory"),
    ("ge", "Geometry"),
    ("co", "Combinatorics")
)

QUESTION_TYPES = (
    ("co", "Correct"),
    ("es", "Estimation")
)


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

    def __str__(self):
        return "Team[{}]".format(self.name)


class Student(models.Model):
    """A student participating in the competition."""

    name = models.CharField(max_length=256, blank=True)
    subject1 = models.CharField(max_length=2, blank=True, choices=SUBJECT_CHOICES, verbose_name="Subject 1")
    subject2 = models.CharField(max_length=2, blank=True, choices=SUBJECT_CHOICES, verbose_name="Subject 2")
    team = models.ForeignKey(Team, related_name="students")

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return "Student[{}]".format(self.name)


class Competition(models.Model):
    """An competition question container."""

    name = models.CharField(max_length=128)
    year = models.IntegerField()

    def __init__(self, name, year):
        """Initialize a new competition."""

        super().__init__()
        self.name = name
        self.year = year


class Round(models.Model):
    """A single competition round."""

    competition = models.ForeignKey(Competition, related_name="rounds")
    name = models.CharField(max_length=64)
    individual = models.BooleanField()

    def __init__(self, competition, name, individual):
        """Initialize a new round."""

        super().__init__()
        self.competition = competition
        self.name = name
        self.individual = individual


class Question(models.Model):
    """A question container model."""

    round = models.ForeignKey(Round, related_name="questions")
    label = models.CharField(max_length=32)
    type = models.CharField(max_length=2, choices=QUESTION_TYPES)

    def __init__(self, round, label, type):
        """Initialize a new question."""

        super().__init__()
        self.round = round
        self.label = label
        self.type = type


class Answer(models.Model):
    """An answer to a question."""

    question = models.ForeignKey(Question, related_name="answers")
    student = models.ForeignKey(Student, related_name="answers")
    team = models.ForeignKey(Team, related_name="answers")
    value = models.FloatField()

    def points(self):
        """Calculate the raw number of points received for the question."""

        return self.value
