from django.forms import Form, ModelForm, ValidationError, CharField, inlineformset_factory, BaseInlineFormSet, PasswordInput
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


class LoginForm(PrettyForm):
    username = CharField()
    password = CharField(widget=PasswordInput)

    def clean(self):
        self.user = authenticate(username=self.cleaned_data['username'], password=self.cleaned_data['password'])

        if self.user is None:
            raise ValidationError("Login was unsuccessful!")

        return self.cleaned_data