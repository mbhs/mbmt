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

    @property
    def division_name(self):
        return dict(_DIVISIONS).get(self.division)


class Student(models.Model):
    """A student participating in the competition."""

    name = models.CharField(max_length=256, blank=True)
    subject1 = models.CharField(max_length=2, blank=True, choices=_SUBJECT_CHOICES, verbose_name="Subject 1")
    subject2 = models.CharField(max_length=2, blank=True, choices=_SUBJECT_CHOICES, verbose_name="Subject 2")
    team = models.ForeignKey(Team, related_name="students")

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

    def __init__(self, id, name, year, active=False):
        """Initialize a new competition."""

        super().__init__()
        self.id = id
        self.name = name
        self.year = year
        self.active = active

    def __repr__(self):
        """Represent the competition as a string."""

        return "Competition[{}]".format(self.name)

    def save_all(self):
        """Save self and all rounds and questions."""

        self.save()
        for round in self.rounds:
            round.save_all()


class Round(models.Model):
    """A single competition round."""

    competition = models.ForeignKey(Competition, related_name="rounds")
    name = models.CharField(max_length=64)
    _grouping = models.IntegerField(choices=_ROUND_GROUPINGS)

    def __init__(self, competition, name, grouping):
        """Initialize a new round."""

        super().__init__()
        self.competition = competition
        self.name = name
        self.grouping = grouping

    @property
    def grouping(self):
        """Get the grouping as a string."""

        return ROUND_GROUPINGS[self._grouping]

    @grouping.setter
    def grouping(self, value):
        """Set the value of grouping as a string."""

        assert type(value) == str
        self._grouping = ROUND_GROUPINGS[value]

    def save_all(self):
        """Save self and all questions."""

        self.save()
        for question in self.questions:
            question.save()


class Question(models.Model):
    """A question container model."""

    round = models.ForeignKey(Round, related_name="questions")
    label = models.CharField(max_length=32)
    _type = models.IntegerField(choices=_QUESTION_TYPES)

    def __init__(self, round, label, type):
        """Initialize a new question."""

        super().__init__()
        self.round = round
        self.label = label
        self.type = type

    @property
    def type(self):
        """Get the type of question."""

        return QUESTION_TYPES[self._type]

    @type.setter
    def type(self, value):
        """Set the type of question as a string."""

        assert type(value) == str
        self._type = QUESTION_TYPES[value]


class Answer(models.Model):
    """An answer to a question."""

    question = models.ForeignKey(Question, related_name="answers")
    student = models.ForeignKey(Student, related_name="answers")
    team = models.ForeignKey(Team, related_name="answers")
    value = models.FloatField()
