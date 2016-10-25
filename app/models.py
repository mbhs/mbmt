from django.db import models


SUBJECTS = ["Algebra", "Number Theory", "Geometry", "Combinatorics"]


class School(models.Model):
    name = models.CharField(max_length=256)
    sponsor = models.CharField(max_length=256)
    email = models.EmailField()

    code = models.CharField(max_length=32)

    user = models.OneToOneField('auth.User', related_name="school")


class Team(models.Model):
    name = models.CharField(max_length=256)
    school = models.ForeignKey(School, related_name="teams")


class Student(models.Model):
    name = models.CharField(max_length=256)
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

    category1 = models.CharField(max_length=2, choices=SUBJECTS)
    category2 = models.CharField(max_length=2, choices=SUBJECTS)