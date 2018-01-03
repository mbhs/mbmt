from django.contrib import admin

from . import models


class CompetitionAdmin(admin.ModelAdmin):
    """Administrative view for the competition model."""

    list_display = ["id", "name", "date", "active"]
    ordering = ["active", "name"]
    actions = ["set_active"]

    def set_active(self, request, queryset):
        """Set a competition as active."""

        queryset.first().activate()


admin.site.register(models.Competition, CompetitionAdmin)
