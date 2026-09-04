from django import forms

from workout.models import Workout


class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ('name',)

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        if Workout.objects.filter(
            user=self.user,
            name__iexact=name,
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                'You already have a workout plan with this name.'
            )

        return name
