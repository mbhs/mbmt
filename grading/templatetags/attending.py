from django import template


register = template.Library()


ICON_YES = u"""<img src="/static/admin/img/icon-yes.svg">"""
ICON_NO = u"""<img src="/static/admin/img/icon-no.svg">"""


@register.filter(is_safe=True)
def attending(student):
    """Whether a student is attending."""

    if student.attending:
        return ICON_YES
    return ICON_NO


attending.is_safe = True
