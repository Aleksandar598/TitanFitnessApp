from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django import forms
from django.forms import DateInput
from users.models import CustomUser
from users.validators import validate_minimum_weight, validate_maximum_weight, validate_birth_date,  validate_realistic_height


class CreateUserForm(UserCreationForm):
    fitness_goal = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput,
    )

    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields +('email', 'birth_date', 'height', 'gender', 'current_weight', 'target_weight','fitness_goal', 'activity_level')
        widgets = {
            'birth_date': DateInput(attrs={'class': 'form-control', 'type' : 'date'}, format='%Y-%m-%d'),
        }


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Email already registered")
        return email

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        validate_birth_date(birth_date)
        return birth_date

    def clean_height(self):
        height = self.cleaned_data.get('height')
        validate_realistic_height(height)
        return height

    def clean_current_weight(self):
        weight = self.cleaned_data.get('current_weight')
        validate_minimum_weight(weight)
        validate_maximum_weight(weight)
        return weight

    def clean_target_weight(self):
        weight = self.cleaned_data.get('target_weight')
        validate_minimum_weight(weight)
        validate_maximum_weight(weight)
        return weight

    def clean(self):
        cleaned_data = super().clean()

        current_weight = cleaned_data.get('current_weight')
        target_weight = cleaned_data.get('target_weight')
        if current_weight is None or target_weight is None:
            return cleaned_data
        if target_weight < current_weight:
            cleaned_data['fitness_goal'] = -250
        elif target_weight > current_weight:
            cleaned_data['fitness_goal'] = 250
        else:
            cleaned_data['fitness_goal'] = 0

        return cleaned_data

