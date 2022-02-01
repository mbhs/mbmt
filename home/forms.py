from django import forms
from django.contrib.auth import authenticate
from crispy_forms.helper import FormHelper


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
