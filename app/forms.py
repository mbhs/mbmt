from django.forms import Form, ModelForm, ValidationError, CharField, inlineformset_factory, BaseInlineFormSet
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from app import models

from crispy_forms.helper import FormHelper


class PrettyHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(PrettyHelper, self).__init__(*args, **kwargs)
        self.form_tag = False
        self.html5_required = True


class PrettyForm(Form):
    helper = PrettyHelper()


class RegisterForm(PrettyForm, ModelForm):
    school_name = CharField(max_length=256)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'email']


class TeamForm(PrettyForm, ModelForm):
    class Meta:
        model = models.Team
        fields = ['name']


class StudentInlineFormSet(BaseInlineFormSet):
    pass


StudentFormSet = inlineformset_factory(models.Team, models.Student, fields=['name', 'subject1', 'subject2'],
                                       can_delete=False, extra=5, formset=StudentInlineFormSet)


class LoginForm(PrettyForm, ModelForm):
    class Meta:
        model = models.School
        fields = ['code']

    def clean_code(self):
        data = self.cleaned_data['code']
        self.school = authenticate(code=data)

        if self.school is None:
            raise ValidationError("Token not found!")

        return data