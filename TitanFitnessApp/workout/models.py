from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Exercise(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    muscle_group = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='custom_exercises',
    )

    class Meta:
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('created_by', 'name'),
                name='unique_personal_exercise_name_per_user',
            ),
        ]

    @property
    def is_catalog_exercise(self):
        return self.created_by_id is None

    def clean(self):
        super().clean()
        duplicates = Exercise.objects.filter(
            name__iexact=self.name,
            created_by=self.created_by,
        ).exclude(pk=self.pk)
        if duplicates.exists():
            raise ValidationError({'name': 'An exercise with this name already exists in this catalog.'})

    def __str__(self):
        return self.name if self.is_catalog_exercise else f'{self.name} (personal)'


class Workout(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workouts',
    )
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(fields=('user', 'name'), name='unique_workout_name_per_user'),
        ]

    def __str__(self):
        return self.name


class WorkoutExercise(models.Model):

    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='workout_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT, related_name='workout_uses')
    position = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ('position', 'id')
        constraints = [
            models.UniqueConstraint(fields=('workout', 'exercise'), name='unique_exercise_per_workout'),
            models.UniqueConstraint(fields=('workout', 'position'), name='unique_workout_exercise_position'),
        ]

    def __str__(self):
        return f'{self.workout}: {self.exercise}'


class WorkoutExerciseSet(models.Model):
    
    workout_exercise = models.ForeignKey(
        WorkoutExercise,
        on_delete=models.CASCADE,
        related_name='sets',
    )
    set_number = models.PositiveIntegerField()
    weight = models.FloatField(validators=[MinValueValidator(0.0)])
    repetitions = models.PositiveIntegerField()

    class Meta:
        ordering = ('set_number',)
        constraints = [
            models.UniqueConstraint(
                fields=('workout_exercise', 'set_number'),
                name='unique_set_number_per_workout_exercise',
            ),
        ]

    def __str__(self):
        return f'{self.workout_exercise} — set {self.set_number}'
