from django import forms
from django.db.models import Q

from workout.models import Exercise, WorkoutSessionExercise


class WorkoutSessionExerciseForm(forms.ModelForm):
    class Meta:
        model = WorkoutSessionExercise
        fields = ('exercise',)

    def __init__(self, *args, user, workout_session, **kwargs):
        super().__init__(*args, **kwargs)
        self.workout_session = workout_session
        self.fields['exercise'].queryset = Exercise.objects.filter(
            Q(created_by__isnull=True) | Q(created_by=user),
        )

    def clean_exercise(self):
        exercise = self.cleaned_data['exercise']
        if self.workout_session.session_exercises.filter(exercise=exercise).exists():
            raise forms.ValidationError('This exercise has already been added to the session.')
        return exercise
