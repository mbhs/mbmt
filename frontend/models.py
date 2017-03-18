from django.db import models
from django.contrib.auth.models import User


SUBJECT_CHOICES = (
    ("al", "Algebra"),
    ("nt", "Number Theory"),
    ("ge", "Geometry"),
    ("cp", "Counting and Probability"))

DIVISIONS = (
    (1, "Pascal"),
    (2, "Ramanujan"))
DIVISIONS_MAP = {1: "Pascal", 2: "Ramanujan"}

SHIRT_SIZES = (
    (0, "Default"),
    (1, "Adult Small"),
    (2, "Adult Medium"),
    (3, "Adult Large"),
    (4, "Adult Extra Large"))


class Competition(models.Model):
    """An competition question container.

    The competition must defined here instead of grading to avoid
    circular imports. This prevents the competition from having a
    round instantiation method, so both that and the question
    convenience constructor have been shifted down to the Round and
    Question objects.
    """

    id = models.CharField(max_length=12, primary_key=True)
    name = models.CharField(max_length=128)
    date = models.DateField()
    active = models.BooleanField(default=False)

    # Competition dates
    date_registration_start = models.DateField()
    date_registration_end = models.DateField()
    date_team_add_end = models.DateField()
    date_shirt_order_end = models.DateField()

    def __repr__(self):
        """Represent the competition as a string."""

        return "Competition[{}]".format(self.name)

    @staticmethod
    def current():
        """Get the active competition."""

        return Competition.objects.filter(active=True).first()

    @staticmethod
    def activate(competition):
        """Set a competition as active."""

        for active in Competition.objects.filter(active=True):
            active.active = False
            active.save()
        competition.active = True
        competition.save()


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
    competition = models.ForeignKey(Competition, related_name="teams")
    division = models.IntegerField(choices=DIVISIONS)

    def __str__(self):
        """Represent the team as a string."""

        return "Team[{}]".format(self.name)

    @staticmethod
    def current():
        """Get the teams for the current competition."""

        return Team.objects.filter(competition=Competition.current())


class Student(models.Model):
    """A student participating in the competition."""

    name = models.CharField(max_length=256, blank=True)
    # TODO: possibly implement first and last name
    # first_name = models.CharField(max_length=64)
    # last_name = models.CharField(max_length=64)
    subject1 = models.CharField(max_length=2, blank=True, choices=SUBJECT_CHOICES, verbose_name="Subject 1")
    subject2 = models.CharField(max_length=2, blank=True, choices=SUBJECT_CHOICES, verbose_name="Subject 2")
    team = models.ForeignKey(Team, related_name="students")
    size = models.IntegerField(choices=SHIRT_SIZES, default=0)
    attending = models.BooleanField(default=False)

    class Meta:
        """Meta information about the student."""

        ordering = ('name',)

    def __str__(self):
        """Represent the student as a string."""

        return "Student[{}]".format(self.name)
