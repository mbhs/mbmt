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

    class Meta:
        permissions = (
            ('can_grade', "Can grade student answers"),
        )


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