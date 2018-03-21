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

    list_display = ["name", "school_name", "sponsor_name", "division"]
    ordering = ["school", "name"]

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


admin.site.register(models.School, SchoolAdmin)
admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.Chaperone)
admin.site.register(models.Student)
