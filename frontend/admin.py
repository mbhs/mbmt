from django.contrib import admin

from . import models


class CompetitionAdmin(admin.ModelAdmin):
    """Administrative view for the competition model."""

    list_display = ["id", "name", "date", "active"]
    ordering = ["active", "name"]
    actions = ["set_active"]

    def set_active(self, request, queryset):
        """Set a competition as active."""

        models.Competition.activate(queryset.first())


class SchoolAdmin(admin.ModelAdmin):
    """Administrative view for school model."""

    list_display = ["name", "team_count", "sponsor_name"]
    ordering = ["name"]

    def team_count(self, obj):
        """Get the team names of the school."""

        return models.Team.objects.filter(school=obj).count()

    def sponsor_name(self, obj):
        """Get the sponsor of the school."""

        return "{} {}".format(obj.user.first_name, obj.user.last_name)


class TeamAdmin(admin.ModelAdmin):
    """Administrative view for team model."""

    list_display = ["name", "school_name", "sponsor_name", "division"]
    ordering = ["school", "name"]

    def school_name(self, obj: models.Team):
        """Get the school name."""

        return obj.school.name

    def sponsor_name(self, obj):
        """Get the sponsor name of the school."""

        return "{} {}".format(obj.school.user.first_name, obj.school.user.last_name)


admin.site.register(models.Competition, CompetitionAdmin)
admin.site.register(models.School, SchoolAdmin)
admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.Student)
