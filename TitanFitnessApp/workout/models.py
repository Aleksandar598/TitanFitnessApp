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
    is_active = models.BooleanField(default=True)

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


class WorkoutPlanExerciseSet(models.Model):
    workout_exercise = models.ForeignKey(
        WorkoutExercise,
        on_delete=models.CASCADE,
        related_name='planned_sets',
    )
    set_number = models.PositiveIntegerField()
    weight = models.FloatField(
        validators=[MinValueValidator(0.0)],
    )
    repetitions = models.PositiveIntegerField()

    class Meta:
        ordering = ('set_number',)
        constraints = [
            models.UniqueConstraint(
                fields=('workout_exercise', 'set_number'),
                name='unique_set_number_per_workout_plan_exercise',
            ),
        ]

    def __str__(self):
        return (
            f'{self.workout_exercise} '
            f'— planned set {self.set_number}'
        )


class WorkoutExerciseSet(models.Model):
    
    workout_session_exercise = models.ForeignKey(
        'WorkoutSessionExercise',
        on_delete=models.CASCADE,
        related_name='sets',
    )
    set_number = models.PositiveIntegerField()
    weight = models.FloatField(validators=[MinValueValidator(0.0)])
    repetitions = models.PositiveIntegerField()
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ('set_number',)
        constraints = [
            models.UniqueConstraint(
                fields=('workout_session_exercise', 'set_number'),
                name='unique_set_number_per_workout_session_exercise',
            ),
        ]

    def __str__(self):
        return f'{self.workout_session_exercise} — set {self.set_number}'


class WorkoutSession(models.Model):

    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workout_sessions',
    )
    workout = models.ForeignKey(
        Workout,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='sessions',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    calories_burned = models.PositiveIntegerField(default=0, null=True, blank=True)

    class Meta:
        ordering = ('-started_at',)

    def __str__(self):
        return f'{self.user} — session started {self.started_at:%Y-%m-%d %H:%M}'

    def set_calories(self):
        total_volume = 0
        total_repetitions = 0
        k = 1

        for session_exercise in self.session_exercises.prefetch_related('sets'):
            for workout_set in session_exercise.sets.filter(is_completed=True):
                total_volume += workout_set.weight * workout_set.repetitions
                total_repetitions += workout_set.repetitions

        body_weight = self.user.current_weight

        self.calories_burned = round((total_volume + ( total_repetitions * body_weight * k )) * 0.014)


class PersonalExerciseRecord(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exercise_records',
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.PROTECT,
        related_name='personal_records',
    )
    weight = models.FloatField(
        validators=[MinValueValidator(0.0)],
    )
    repetitions = models.PositiveIntegerField()
    achieved_at = models.DateTimeField(auto_now_add=True)
    workout_session = models.ForeignKey(
        WorkoutSession,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='exercise_records',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'exercise'),
                name='unique_personal_record_per_exercise',
            ),
        ]

    def __str__(self):
        return (
            f'{self.user} — {self.exercise}: '
            f'{self.weight} kg × {self.repetitions}'
        )


class WorkoutSessionExercise(models.Model):

    workout_session = models.ForeignKey(
        WorkoutSession,
        on_delete=models.CASCADE,
        related_name='session_exercises',
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT, related_name='session_uses')
    position = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ('position', 'id')
        constraints = [
            models.UniqueConstraint(
                fields=('workout_session', 'exercise'),
                name='unique_exercise_per_workout_session',
            ),
            models.UniqueConstraint(
                fields=('workout_session', 'position'),
                name='unique_workout_session_exercise_position',
            ),
        ]

    def __str__(self):
        return f'{self.workout_session}: {self.exercise}'
