from django.db import models
from django.contrib.auth.models import User


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
    date_team_edit_end = models.DateField()
    date_shirt_order_end = models.DateField()

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
