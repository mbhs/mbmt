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

    username = forms.EmailField(max_length=60, label="Email address")
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"id": "password"}))
    password_duplicate = forms.CharField(
        widget=forms.PasswordInput(attrs={"data-match": "#password"}),
        label="Enter password again")

    def clean(self):
        """Clean and process the input."""

        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("password_duplicate"):  # TODO: move to individual field
            raise ValidationError("Passwords do not match")
        cleaned_data["email"] = cleaned_data["username"]
        return cleaned_data

    class Meta:
        """Form metadata and formatting."""

        model = User
        exclude = ["email"]
        fields = ["username", "password", "password_duplicate", "first_name", "last_name"]


class SchoolForm(forms.Form):
    """Form for choosing a school to coach for."""

    school = forms.CharField(max_length=60, min_length=1)
    other = forms.CharField(max_length=60, required=False)

    def __init__(self, *args, **kwargs):
        """Override to add an other field."""

        super().__init__(*args, **kwargs)
        self.use_other = False

    def clean(self):
        """Clean and validate the form."""

        cleaned_data = super().clean()

        # Check other
        if cleaned_data.get("school") == "other":
            self.use_other = True
            if len(cleaned_data.get("other", "")) == 0:
                raise ValidationError("You must enter another school name")
            cleaned_data["school"] = cleaned_data["other"]

        # Check school exists
        else:
            if not models.School.objects.filter(name=cleaned_data.get("school")).exists():
                raise ValidationError("School does not exist")

        return cleaned_data


class TeamForm(PrettyForm, forms.ModelForm):
    """Form for creating a new team."""

    def __init__(self, *args, **kwargs):
        """Initialize the team form and modify the empty label."""

        super().__init__(*args, **kwargs)
        divisions = [("", "Choose...")] + self.fields["division"].choices[1:]
        divisions[1] = divisions[1][0], divisions[1][1] + " (harder)"
        self.fields["division"].choices = divisions
        self.fields["name"].widget.attrs["placeholder"] = "Official Team Name"

    class Meta:
        """Form metadata and formatting."""

        model = models.Team
        fields = ["name", "division"]


class StudentForm(forms.ModelForm):
    """Inline form for a single student."""

    def __init__(self, *args, **kwargs):
        """Initialize and modify fields."""

        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs["placeholder"] = "First"
        self.fields["last_name"].widget.attrs["placeholder"] = "Last"
        self.fields["subject1"].choices = [("", "Choose...")] + self.fields["subject1"].choices[1:]
        self.fields["subject2"].choices = [("", "Choose...")] + self.fields["subject2"].choices[1:]
        self.fields["shirt_size"].choices = [("", "Choose...")] + self.fields["shirt_size"].choices[1:]
        self.fields["grade"].choices = [("", "Choose...")] + self.fields["grade"].choices[1:]

    def clean(self):
        """Clean and validate student data."""

        cleaned_data = super().clean()
        if any(cleaned_data.values()):
            if not cleaned_data["first_name"] or not cleaned_data["last_name"]:
                raise ValidationError("A first and last name is required.")
            if not cleaned_data["subject1"] or not cleaned_data["subject2"]:
                raise ValidationError("Two subjects are required for {} {}.".format(
                    cleaned_data["first_name"], cleaned_data["last_name"]))
            if cleaned_data["subject1"] == cleaned_data["subject2"]:
                raise ValidationError("The subject tests for {} {} must be different.".format(
                    cleaned_data["first_name"], cleaned_data["last_name"]))
        return cleaned_data

    class Meta:
        """Form metadata and formatting."""

        model = models.Student
        fields = ["first_name", "last_name", "subject1", "subject2", "grade", "shirt_size"]


# Form factory for multiple students on a single team
NaiveStudentFormSet = forms.modelformset_factory(
    models.Student,
    form=StudentForm,
    min_num=1,
    max_num=5,
    extra=5,
    validate_min=False)


class StudentFormSet(NaiveStudentFormSet):
    """Multiple student editor for the main team editing form."""

    def clean(self):
        """Clean and validate student data."""

        data = super().clean()
        for form in self:
            form.clean()

        students = [form.instance for form in self if form.instance.first_name]
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
        return data


class ChaperoneForm(PrettyForm, forms.ModelForm):
    """Simple chaperone entry."""

    def __init__(self, *args, **kwargs):
        """Initialize and modify fields."""

        super().__init__(*args, **kwargs)
        self.fields["shirt_size"].choices = [("", "Choose...")] + self.fields["shirt_size"].choices[1:]

    class Meta:
        model = models.Chaperone
        fields = ["first_name", "last_name", "email", "phone", "shirt_size"]
