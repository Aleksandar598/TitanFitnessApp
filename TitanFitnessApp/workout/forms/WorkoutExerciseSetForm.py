from django import forms

from workout.models import WorkoutExerciseSet


class WorkoutExerciseSetForm(forms.ModelForm):
    class Meta:
        model = WorkoutExerciseSet
        fields = ('weight', 'repetitions')
        widgets = {
            'weight': forms.NumberInput(attrs={'min': '0', 'step': '0.5'}),
            'repetitions': forms.NumberInput(attrs={'min': '1', 'step': '1'}),
        }

    def clean_repetitions(self):
        repetitions = self.cleaned_data['repetitions']
        if repetitions <= 0:
            raise forms.ValidationError('Repetitions must be greater than 0.')
        return repetitions
