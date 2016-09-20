from django.forms import ModelForm, ValidationError
from django.contrib.auth import authenticate

from app import models

from crispy_forms.helper import FormHelper


class PrettyForm(ModelForm):
    helper = FormHelper()
    helper.form_tag = False
    helper.html5_required = True


class RegisterForm(PrettyForm):
    class Meta:
        model = models.School
        fields = ['name', 'sponsor', 'email']


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