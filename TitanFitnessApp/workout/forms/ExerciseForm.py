from django import forms

from workout.models import Exercise


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ('name', 'description', 'muscle_group')

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if Exercise.objects.filter(created_by=self.user, name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('You already have a personal exercise with this name.')
        return name
