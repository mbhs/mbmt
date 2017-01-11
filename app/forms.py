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
    """School sponsor registration form.

    To simplify registration and team management, the username field
    has effectively been replaced by the email field. In other words,
    users log in with their emails. This form makes that work.
    """

    username = forms.EmailField(max_length=64, label="Email address")
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
        exclude = ["email"]
        fields = ["username", "password", "password_duplicate", "first_name", "last_name", "school_name"]


class TeamForm(PrettyForm, forms.ModelForm):
    """Form for creating a new team."""

    class Meta:
        model = models.Team
        fields = ["name"]


class StudentForm(forms.ModelForm):

    def is_valid(self):
        """Clean and validate student data."""

        is_valid = super().is_valid()
        if self.cleaned_data["name"].strip():
            is_valid = is_valid and self.cleaned_data["subject1"] != self.cleaned_data["subject2"]
        return is_valid

    class Meta:
        model = models.Student
        fields = ["name", "subject1", "subject2"]


StudentFormSet = forms.modelformset_factory(
    models.Student,
    form=StudentForm,
    min_num=5,
    max_num=5)


class LoginForm(PrettyForm):
    """Login form for graders and sponsors.

    Note that as a result of the registration process, usernames
    conform to email field standards. Login still works.
    """

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
