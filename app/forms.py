from django.forms import ModelForm, ValidationError, CharField
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from app import models

from crispy_forms.helper import FormHelper


class PrettyForm(ModelForm):
    helper = FormHelper()
    helper.form_tag = False
    helper.html5_required = True


class RegisterForm(PrettyForm):
    school_name = CharField(max_length=128)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'email']


class LoginForm(PrettyForm):
    class Meta:
        model = models.School
        fields = ['code']

    def clean_code(self):
        data = self.cleaned_data['code']
        self.school = authenticate(code=data)

        if self.school is None:
            raise ValidationError("Token not found!")

        return data