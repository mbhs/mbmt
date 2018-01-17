from django.db import models
from django.contrib.auth.models import User

from home.models import Competition


SUBJECTS = (
    ("al", "Algebra"),
    ("nt", "Number Theory"),
    ("ge", "Geometry"),
    ("cp", "Counting and Probability"))
SUBJECTS_MAP = dict(SUBJECTS)

DIVISIONS = (
    (1, "Gauss"),  # Harder
    (2, "Cantor"))
DIVISIONS_MAP = dict(DIVISIONS)

SHIRT_SIZES = (
    (0, "Default"),
    (1, "Adult Small"),
    (2, "Adult Medium"),
    (3, "Adult Large"),
    (4, "Adult Extra Large"))


class School(models.Model):
    """A simple school model that is represented by a teacher."""

    name = models.CharField(max_length=60)
    coaches = models.ManyToManyField(User, related_name="school", through="Coaching")

    def __str__(self):
        """Represent the school as a string."""

        return "School[{}]".format(self.name)

    def current_teams(self):
        """Return the current list of teams for the school."""

        return Team.objects.filter(competition__active=True, school=self)

    def current_chaperones(self):
        """Get the current list of chaperons."""

        return


class Coaching(models.Model):
    """Model to indicate which competition the coach is registered for."""

    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="+")
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name="competitions")


class Team(models.Model):
    """Represents a team of students competing in the competition."""

    name = models.CharField(max_length=256)
    number = models.IntegerField(default=0)
    school = models.ForeignKey(School, related_name="teams")
    competition = models.ForeignKey(Competition, related_name="teams")
    division = models.IntegerField(choices=DIVISIONS)

    def __str__(self):
        """Represent the team as a string."""

        return "Team[{}]".format(self.name)

    @staticmethod
    def current():
        """Get the teams for the current competition."""

        return Team.objects.filter(competition__active=True)

    def get_students_display(self):
        """Get the comma separated list of students."""

        return ", ".join(map(lambda x: x.name, self.students.all()))


class Student(models.Model):
    """A student participating in the competition."""

    # TODO: possibly implement first and last name
    # first_name = models.CharField(max_length=64)
    # last_name = models.CharField(max_length=64)

    name = models.CharField(max_length=64, blank=True)
    team = models.ForeignKey(Team, related_name="students")
    subject1 = models.CharField(max_length=2, blank=True, choices=SUBJECTS, verbose_name="Subject 1")
    subject2 = models.CharField(max_length=2, blank=True, choices=SUBJECTS, verbose_name="Subject 2")

    size = models.IntegerField(choices=SHIRT_SIZES, default=0)
    attending = models.BooleanField(default=False)

    class Meta:
        """Meta information about the student."""

        ordering = ('name',)

    def __str__(self):
        """Represent the student as a string."""

        return "Student[{}]".format(self.name)

    @staticmethod
    def current():
        """Get the students in the current competition."""

        return Student.objects.filter(team__competition__active=True)


class Chaperone(models.Model):
    """A chaperone for a team."""
