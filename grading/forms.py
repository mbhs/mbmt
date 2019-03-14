from django import forms
from crispy_forms.helper import FormHelper


from home.forms import PrettyForm
from home.models import Competition


class StatsForm(PrettyForm):
    """Form for viewing stats."""

    choice_list = [('','Choose a year')]+[(x.pk, x.name) for x in Competition.objects.all()]
    year = forms.ChoiceField(choices = choice_list,widget=forms.Select(attrs={"onChange":'this.form.submit();','style':'width:200px'}))
