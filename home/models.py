from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Competition(models.Model):
    """An competition question container.

    The competition must defined here instead of grading to avoid
    circular imports. This prevents the competition from having a
    round instantiation method, so both that and the question
    convenience constructor have been shifted down to the Round and
    Question objects.
    """

    name = models.CharField(max_length=128)
    date = models.DateField()
    active = models.BooleanField(default=False)

    # Competition dates
    date_registration_start = models.DateField()
    date_registration_end = models.DateField()
    date_edit_teams_end = models.DateField()
    date_edit_shirts_end = models.DateField()

    # Semantics
    year = models.CharField(max_length=20)  # First, second, etc.

    # Grader cache
    _graders = {}

    def __repr__(self):
        """Represent the competition as a string."""

        return "Competition[{}]".format(self.name)

    __str__ = __repr__

    @staticmethod
    def current():
        """Get the active competition."""

        return Competition.objects.filter(active=True).first()

    def activate(self):
        """Set a competition as active."""

        for active in Competition.objects.filter(active=True):
            active.active = False
            active.save()
        self.active = True
        self.save()

    @property
    def grader(self):
        """Instantiate a grader of the competition type."""

        try:
            return self._graders[self.id]
        except KeyError:
            import importlib
            grader = importlib.import_module("competitions.{}.grading".format(self.id)).Grader(self)
            self._graders[self.id] = grader
            return grader

    @property
    def can_register(self):
        """Check if now is within the registration period."""

        return self.date_registration_start <= timezone.now().date() <= self.date_registration_end

    @property
    def can_edit_teams(self):
        """Check if now is within the team editing period."""

        return self.date_registration_start <= timezone.now().date() <= self.date_edit_teams_end

    @property
    def can_edit_shirts(self):
        """Check if now is within the shirt editing period."""

        return self.date_registration_start <= timezone.now().date() <= self.date_edit_shirts_end


class Organizer(models.Model):
    """Organizers for the about page."""

    image = models.ImageField(blank=True, null=True, upload_to="media/people/%Y/")
    order = models.IntegerField(default=0)
    name = models.CharField(max_length=50)
    role = models.CharField(max_length=20)


class Writer(models.Model):
    """Problem writers."""

    name = models.CharField(max_length=50)
