from django import forms

from workout.models import WorkoutPlanExerciseSet


class WorkoutPlanExerciseSetForm(forms.ModelForm):
    class Meta:
        model = WorkoutPlanExerciseSet
        fields = ('weight', 'repetitions')
        widgets = {
            'weight': forms.NumberInput(
                attrs={'min': '0', 'step': '0.5'},
            ),
            'repetitions': forms.NumberInput(
                attrs={'min': '1', 'step': '1'},
            ),
        }

    def clean_repetitions(self):
        repetitions = self.cleaned_data['repetitions']

        if repetitions <= 0:
            raise forms.ValidationError(
                'Repetitions must be greater than zero.'
            )

        return repetitions
