from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper

from frontend import models


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
    has effectively been replaced by the email field.
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
        if models.User.objects.filter(username=cleaned_data["username"]).exists():
            raise ValidationError("Username is already taken.")
        return cleaned_data

    class Meta:
        """Form metadata and formatting."""

        model = User
        exclude = ["email"]
        fields = ["username", "password", "password_duplicate", "first_name", "last_name", "school_name"]


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


class LoginForm(PrettyForm):
    """Login form for graders and sponsors.

    Note that as a result of the registration process, usernames
    conform to email field standards. Login still works.
    """

    username = forms.CharField(label="Email address")
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
