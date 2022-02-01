from django.contrib import admin

from . import models


class SchoolAdmin(admin.ModelAdmin):
    """Administrative view for school model."""

    list_display = ["name", "team_count", "sponsor_name"]
    ordering = ["name"]

    def team_count(self, obj):
        """Get the team names of the school."""

        return models.Team.current(school=obj).count()

    def sponsor_name(self, obj):
        """Get the sponsor of the school."""

        try:
            coaching = models.Coaching.current(school=obj).get()
            coach = coaching.coach
            return "{} {}".format(coach.first_name, coach.last_name)
        except models.Coaching.DoesNotExist:
            return ""


class TeamAdmin(admin.ModelAdmin):
    """Administrative view for team model."""

    list_display = ["name", "school_name", "sponsor_name", "division", "competition_name"]
    ordering = ["-competition__name", "school", "name"]

    def school_name(self, obj: models.Team):
        """Get the school name."""

        return obj.school.name

    def sponsor_name(self, obj):
        """Get the sponsor name of the school."""

        try:
            coaching = models.Coaching.current(school=obj.school).get()
            coach = coaching.coach
            return "{} {}".format(coach.first_name, coach.last_name)
        except models.Coaching.DoesNotExist:
            return ""

    def competition_name(self, obj: models.Team):
        """"Get the competition year"""

        return obj.competition.name


class StudentAdmin(admin.ModelAdmin):
    """Administrative view for the student model."""

    list_display = ["last_name", "first_name", "grade", "team_name", "team_division", "school_name", "competition_name"]
    ordering = ["-team__competition__name", "team__school", "team__name", "last_name", "first_name"]

    def team_name(self, obj: models.Student):
        """Get student's team name."""

        return obj.team.name

    def team_division(self, obj: models.Student):
        """Get student division"""

        return obj.team.division

    def school_name(self, obj: models.Student):
        """Get student's school"""

        return obj.team.school.name

    def competition_name(self, obj: models.Student):
        """Get student's competition year"""

        return obj.team.competition.name


admin.site.register(models.School, SchoolAdmin)
admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.Chaperone)
admin.site.register(models.Student, StudentAdmin)
