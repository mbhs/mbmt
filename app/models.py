"""Models for the competition and response."""

from django.db import models


SUBJECT_CHOICES = (
    ("AL", "Algebra"),
    ("NT", "Number Theory"),
    ("GE", "Geometry"),
    ("CO", "Combinatorics")
)

QUESTION_TYPES = (
    ("B", "Boolean"),
    ("R", "Estimation")
)


class School(models.Model):
    """A simple school model that is represented by a teacher."""

    name = models.CharField(max_length=256)
    email = models.EmailField()
    user = models.OneToOneField('auth.User', related_name="school")

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

    name = models.CharField(max_length=256)
    year = models.IntegerField()


class Round(models.Model):
    """A single competition round."""

    individual = models.BooleanField()
    competition = models.ForeignKey(Competition, related_name="rounds")


class Question(models.Model):
    """A question container model."""

    type = models.CharField(max_length=1, choices=QUESTION_TYPES)
    round = models.ForeignKey(Round, related_name="questions")


class Answer(models.Model):
    """An answer to a question."""

    question = models.ForeignKey(Question, related_name="answers")
    student = models.ForeignKey(Student, related_name="answers")
    team = models.ForeignKey(Team, related_name="answers")
    value = models.FloatField()
