from django.contrib import admin

from . import models


class QuestionAdmin(admin.ModelAdmin):
    """Administrative view for the competition model."""

    list_display = ["id", "competition_name", "round_name", "number", "label", "weight"]
    ordering = ["round__competition__name", "round__name", "number"]
    actions = ["number_by_label"]

    def round_name(self, obj):
        """Get the name of the round."""

        return obj.round.name

    def competition_name(self, obj):
        """Get the name of the competition"""

        return obj.round.competition.name

    def number_by_label(self, request, queryset):
        """Set a competition as active."""

        for question in queryset.all():
            try:
                question.number = int(question.label)
                question.save()
            except ValueError:
                pass


admin.site.register(models.Question, QuestionAdmin)
