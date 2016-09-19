from django.forms import ModelForm

from app import models

from crispy_forms.helper import FormHelper


class RegisterForm(ModelForm):
    class Meta:
        model = models.School
        fields = ['name', 'sponsor', 'email']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.html5_required = True