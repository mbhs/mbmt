from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from app import models

from crispy_forms.helper import FormHelper


class PrettyHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(PrettyHelper, self).__init__(*args, **kwargs)
        self.form_tag = False
        self.html5_required = True


class PrettyForm(forms.Form):
    helper = PrettyHelper()


class RegisterForm(PrettyForm, forms.ModelForm):
    school_name = forms.CharField(max_length=256)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'email']


class TeamForm(PrettyForm, forms.ModelForm):
    class Meta:
        model = models.Team
        fields = ['name']


class StudentInlineFormSet(forms.BaseInlineFormSet):
    pass


StudentFormSet = forms.inlineformset_factory(models.Team, models.Student, fields=['name', 'subject1', 'subject2'],
                                       can_delete=False, extra=5, formset=StudentInlineFormSet)


class LoginForm(PrettyForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        self.user = authenticate(username=self.cleaned_data['username'], password=self.cleaned_data['password'])

        if self.user is None:
            raise forms.ValidationError("Login was unsuccessful!")

        return self.cleaned_data


class QuestionsField(forms.Field):
    def __init__(self, schema, **kwargs):
        self.schema = schema
        super(QuestionsField, self).__init__(**kwargs)