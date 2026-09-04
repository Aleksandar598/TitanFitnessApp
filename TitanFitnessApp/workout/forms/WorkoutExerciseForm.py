from django import forms
from django.db.models import Q

from workout.models import Exercise, WorkoutExercise


class WorkoutExerciseForm(forms.ModelForm):
    class Meta:
        model = WorkoutExercise
        fields = ('exercise',)

    def __init__(self, *args, user, workout, **kwargs):
        super().__init__(*args, **kwargs)
        self.workout = workout

        self.fields['exercise'].queryset = Exercise.objects.filter(
            Q(created_by__isnull=True) | Q(created_by=user),
            is_active=True,
        )

    def clean_exercise(self):
        exercise = self.cleaned_data['exercise']

        if self.workout.workout_exercises.filter(
            exercise=exercise,
        ).exists():
            raise forms.ValidationError(
                'This exercise is already in the workout plan.'
            )

        return exercise
