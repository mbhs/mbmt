from django.core.exceptions import ValidationError
from django.db import models

import pickle

SUBJECTS = ["Algebra", "Number Theory", "Geometry", "Combinatorics"]


class School(models.Model):
    name = models.CharField(max_length=256)
    sponsor = models.CharField(max_length=256)
    email = models.EmailField()

    code = models.CharField(max_length=32)

    user = models.OneToOneField('auth.User', related_name="school")

    def __str__(self):
        return "School[{}]".format(self.name)


class Questions:
    @staticmethod
    def check_schema(schema, values):
        types_okay = True
        if not isinstance(values, tuple) or not len(values) == len(schema):
            types_okay = False
            for value, _type in zip(values, schema):
                if _type == bool and value is not None and not isinstance(value, bool):
                    types_okay = False
                if _type == float and value is not None and not isinstance(value, float):
                    types_okay = False

        return types_okay

    @staticmethod
    def blank_from_schema(schema):
        return (None,) * len(schema)

    def __init__(self, schema, serialized=None):
        self.schema = schema

        if serialized is None:
            self.values = (None,) * len(schema)
        else:
            values = pickle.loads(serialized)

            if Questions.check_schema(schema, values):
                self.values = values
            else:
                raise ValidationError("Data did not match schema")


class QuestionsField(models.Field):
    def __init__(self, schema, **kwargs):
        self.schema = schema
        if 'default' not in kwargs:
            kwargs['default'] = Questions.blank_from_schema(schema)
        super(QuestionsField, self).__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(QuestionsField, self).deconstruct()
        kwargs['schema'] = self.schema
        del kwargs['default']
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection, context):
        if isinstance(value, Questions):
            return value
        if value is None:
            return value
        return Questions(self.schema, serialized=value)

    def to_python(self, value):
        if value is None:
            return value
        return Questions(self.schema, serialized=value)

    def get_prep_value(self, value):
        return pickle.dumps(value)

    def get_internal_type(self):
        return 'TextField'

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

    def formfield(self, form_class=None, choices_form_class=None, **kwargs):
        from app import forms
        return forms.QuestionsField(self.schema)


class Team(models.Model):
    name = models.CharField(max_length=256)
    school = models.ForeignKey(School, related_name="teams")

    team = QuestionsField([bool] * 10)
    guts = QuestionsField([bool] * 25 + [float] * 5)

    class Meta:
        permissions = (
            ('can_grade', "Can grade student answers"),
        )

    def __str__(self):
        return "Team[{}]".format(self.name)


class Student(models.Model):
    name = models.CharField(max_length=256, blank=True)
    team = models.ForeignKey(Team, related_name="students")

    ALGEBRA = 'AL'
    NUMBER_THEORY = 'NT'
    GEOMETRY = 'GE'
    COMBINATORICS = 'CO'

    SUBJECTS = (
        (ALGEBRA, "Algebra"),
        (NUMBER_THEORY, "Number Theory"),
        (GEOMETRY, "Geometry"),
        (COMBINATORICS, "Combinatorics")
    )

    subject1 = models.CharField(max_length=2, blank=True, choices=SUBJECTS, verbose_name="Subject 1")
    subject2 = models.CharField(max_length=2, blank=True, choices=SUBJECTS, verbose_name="Subject 2")

    round1 = QuestionsField([bool] * 8)
    round2 = QuestionsField([bool] * 8)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return "Student[{}]".format(self.name)