from django import template


register = template.Library()


@register.filter
def fancy_dict(dictionary):
    """Check the grading status for a team or student by round."""

    return ", ".join(("{}: {}".format(key, value) for key, value in dictionary.items()))
