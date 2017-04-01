from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin

from . import models


# Make sure grading permissions are available
permission = Permission.objects.filter(codename="can_grade").first()
if not permission:
    content_type = ContentType.objects.get_for_model(models.Answer)
    permission = Permission.objects.create(codename="can_grade", name="Can grade", content_type=content_type)
    grading_group, created = Group.objects.get_or_create(name="grading")
    grading_group.permissions.add(permission)


class QuestionAdmin(admin.ModelAdmin):
    """Administrative view for the question model."""

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


class AnswerAdmin(admin.ModelAdmin):
    """Administrative view for answer model."""

    list_display = ["id", "competition_name", "team", "student"]
    actions = ["reset_answer"]

    def competition_name(self, obj):
        """Get the competition of an answer."""

        return obj.question.round.competition.name

    def reset_answer(self, request, queryset):
        """Reset the answers to value none."""

        for answer in queryset.all():
            answer.value = None
            answer.save()


admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.Answer, AnswerAdmin)
