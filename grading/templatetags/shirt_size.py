from django import template

from coaches.models import SHIRT_SIZES_MAP


register = template.Library()


@register.filter
def shirt_size(number):
    """Check the grading status for a team or student by round."""

    return SHIRT_SIZES_MAP[int(number)]
