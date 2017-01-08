from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper

from app import models


class PrettyHelper(FormHelper):
    """Class mixin that handles custom formatting."""

    def __init__(self, *args, **kwargs):
        """Initialize a new pretty form helper."""

        super(PrettyHelper, self).__init__(*args, **kwargs)
        self.form_tag = False
        self.html5_required = True


class PrettyForm(forms.Form):
    """A custom form parent class with the PrettyHelper mixin."""

    helper = PrettyHelper()


class RegisterForm(PrettyForm, forms.ModelForm):
    """School sponsor registration form."""

    school_name = forms.CharField(max_length=256)
    password = forms.CharField(widget=forms.PasswordInput)
    password_duplicate = forms.CharField(widget=forms.PasswordInput, label='Enter password again')

    def clean(self):
        """Clean and process the input."""

        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('password_duplicate'):
            raise ValidationError('Passwords do not match')
        return cleaned_data

    class Meta:
        model = User
        email = {"required": True}
        fields = ["email", "first_name", "last_name"]


class TeamForm(PrettyForm, forms.ModelForm):
    class Meta:
        model = models.Team
        fields = ['name']


class StudentInlineFormSet(forms.BaseInlineFormSet):
    pass


StudentFormSet = forms.inlineformset_factory(
    models.Team,
    models.Student,
    fields=['name', 'subject1', 'subject2'],
    can_delete=False,
    extra=5,
    formset=StudentInlineFormSet)


class LoginForm(PrettyForm):
    """Login form for graders and sponsors."""

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        """Initialize a new login form."""

        super().__init__(*args, **kwargs)
        self.user = None

    def clean(self):
        """Clean and process the input."""

        self.user = authenticate(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'])
        if self.user is None:
            raise forms.ValidationError("Login was unsuccessful!")
        return self.cleaned_data
