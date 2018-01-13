from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from home.forms import PrettyForm
from . import models


class RegisterForm(PrettyForm, forms.ModelForm):
    """School sponsor registration form.

    To simplify registration and team management, the username field
    has effectively been replaced by the email field.
    """

    username = forms.EmailField(max_length=64, label="Email address")
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"id": "password"}))
    password_duplicate = forms.CharField(
        widget=forms.PasswordInput(attrs={"data-match": "#password"}),
        label="Enter password again")

    def clean(self):
        """Clean and process the input."""

        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("password_duplicate"):
            raise ValidationError("Passwords do not match")
        cleaned_data["email"] = cleaned_data["username"]
        return cleaned_data

    class Meta:
        """Form metadata and formatting."""

        model = User
        exclude = ["email"]
        fields = ["username", "password", "password_duplicate", "first_name", "last_name"]


class TeamForm(PrettyForm, forms.ModelForm):
    """Form for creating a new team."""

    class Meta:
        """Form metadata and formatting."""

        model = models.Team
        fields = ["name", "division"]


class StudentForm(forms.ModelForm):
    """Inline form for a single student."""

    def clean(self):
        """Clean and validate student data."""

        cleaned_data = super().clean()
        if any(cleaned_data.values()):
            if not cleaned_data["name"]:
                raise ValidationError("A name is required.")
            if not cleaned_data["subject1"] or not cleaned_data["subject2"]:
                raise ValidationError("Two subjects are required.")
            if cleaned_data["subject1"] == cleaned_data["subject2"]:
                raise ValidationError("The two subjects must be different.")
        return cleaned_data

    class Meta:
        """Form metadata and formatting."""

        model = models.Student
        fields = ["name", "subject1", "subject2", "size"]


# Form factory for multiple students on a single team
NaiveStudentFormSet = forms.modelformset_factory(
    models.Student,
    form=StudentForm,
    min_num=5,
    max_num=5)


class StudentFormSet(NaiveStudentFormSet):
    """Multiple student editor for the main team editing form."""

    def clean(self):
        """Clean and validate student data."""

        students = [form.instance for form in self if form.instance.name]
        if len(students) == 0:
            raise ValidationError("There must be at least one student.")
        subjects = {
            subject: len(list(filter(lambda student: code in (student.subject1, student.subject2), students)))
            for code, subject in models.SUBJECTS}
        if len(students) == 3:
            for subject, count in subjects.items():
                if count < 1:
                    raise ValidationError("There must be at least one student in subject {}.".format(subject))
        elif len(students) == 4:
            for subject, count in subjects.items():
                if count < 1:
                    raise ValidationError("There must be at least one student in subject {}.".format(subject))
                if count > 3:
                    raise ValidationError("There can be at most three items in subject {}.".format(subject))
        elif len(students) == 5:
            for subject, count in subjects.items():
                if count < 2:
                    raise ValidationError("There must be at least two items in subject {}.".format(subject))
