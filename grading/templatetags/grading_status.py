from django import template

from grading.models import Team, Student, Round, Answer


register = template.Library()


ICON_YES = u"""<img src="/static/admin/img/icon-yes.svg">"""
ICON_NO = u"""<img src="/static/admin/img/icon-no.svg">"""
ICON_ALERT = u"""<img src="/static/admin/img/icon-alert.svg">"""


@register.filter(is_safe=True)
def grading_status(team_or_student, round):
    """Check the grading status for a team or student by round."""

    if isinstance(round, str):
        if isinstance(team_or_student, Team):
            round = Round.objects.filter(ref=round, competition=team_or_student.competition).first()
        if isinstance(team_or_student, Student):
            round = Round.objects.filter(ref=round, competition=team_or_student.team.competition).first()

    tags = ""
    if isinstance(team_or_student, Team):
        search = {"team": team_or_student}
    elif isinstance(team_or_student, Student):
        search = {"student": team_or_student}
    else:
        return tags
    if Answer.objects.filter(**search, question__round=round, value__isnull=False).exists():
        tags += ICON_YES
        if Answer.objects.filter(**search, question__round=round, value__isnull=True).exists():
            tags += ICON_ALERT
    else:
        tags += ICON_NO

    return tags


grading_status.is_safe = True
