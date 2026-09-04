from datetime import date
from enum import Enum

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone

# Create your models here.

class FitnessGoal(Enum):
    lose = -250
    maintain = 0
    gain = 250

class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        email = email or f'{username}@admin.local'

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('birth_date', date(1990, 1, 1))
        extra_fields.setdefault('height', 170)
        extra_fields.setdefault('gender', 'male')
        extra_fields.setdefault('current_weight', 70)
        extra_fields.setdefault('target_weight', 70)
        extra_fields.setdefault('fitness_goal', 0)
        extra_fields.setdefault('activity_level', 1.2)

        return super().create_superuser(
            username=username,
            email=email,
            password=password,
            **extra_fields,
        )

class CustomUser(AbstractUser):
    GOAL_CHOICES = [
        (-250, 'Losing Weight'),
        (0, 'Keep Weight'),
        (250, 'Gain Weight'),
    ]
    ACTIVITY_CHOICES = [
        (1.9, 'Very Active'),
        (1.725, 'Active'),
        (1.55, 'Moderate'),
        (1.375, 'Lightly Active'),
        (1.2, 'Sedentary')
    ]
    GENDER_CHOICES = [('male', 'Male' ), ('female', 'Female')]

    email = models.EmailField(max_length=255, unique=True, blank=False, null=False, verbose_name='Email Address')
    birth_date = models.DateField(blank=False, null=False, verbose_name='Birth Date')
    height = models.IntegerField(blank=False, null=False, verbose_name='Height')
    gender = models.CharField(blank=False, null=False, max_length=30, choices=GENDER_CHOICES)
    current_weight = models.IntegerField(blank=False, null=False, verbose_name='Current Weight')
    target_weight = models.IntegerField(blank=False, null=False, verbose_name='Target Weight')
    fitness_goal = models.IntegerField(blank=False, null=False, choices=GOAL_CHOICES, verbose_name='Fitness Goal')
    activity_level = models.FloatField(blank=False, null=False, choices=ACTIVITY_CHOICES, verbose_name='Activity Level')

    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.username

    @property
    def daily_calorie_goal(self):
        bmr = 0
        if self.gender == 'male':
            bmr = 10 * self.current_weight + 6.25 * self.height - 5 * (date.today().year -  self.birth_date.year) + 5
        else:
            bmr = 10 * self.current_weight + 6.25 * self.height - 5 * (date.today().year - self.birth_date.year) - 161

        result_calories = bmr * self.activity_level
        return result_calories + self.fitness_goal

    @property
    def daily_macronutrient_goals(self):
        ratios_by_fitness_goal = {
            FitnessGoal.lose.value: {
                'carbohydrates': 0.40,
                'protein': 0.30,
                'fat': 0.30,
            },
            FitnessGoal.maintain.value: {
                'carbohydrates': 0.50,
                'protein': 0.20,
                'fat': 0.30,
            },
            FitnessGoal.gain.value: {
                'carbohydrates': 0.45,
                'protein': 0.30,
                'fat': 0.25,
            },
        }

        ratios = ratios_by_fitness_goal[self.fitness_goal]
        calorie_goal = self.daily_calorie_goal

        return {
            'calories': round(calorie_goal),
            'protein': round(calorie_goal * ratios['protein'] / 4),
            'carbohydrates': round(
                calorie_goal * ratios['carbohydrates'] / 4
            ),
            'fat': round(calorie_goal * ratios['fat'] / 9),
        }

    def daily_macronutrient_goals_with_workout(
        self,
        workout_calories_burned,
    ):
        base_goals = self.daily_macronutrient_goals
        workout_calories_burned = workout_calories_burned or 0

        return {
            'calories': (
                base_goals['calories']
                + round(workout_calories_burned)
            ),
            'protein': (
                base_goals['protein']
                + round(workout_calories_burned * 0.20 / 4)
            ),
            'carbohydrates': (
                base_goals['carbohydrates']
                + round(workout_calories_burned * 0.60 / 4)
            ),
            'fat': (
                base_goals['fat']
                + round(workout_calories_burned * 0.20 / 9)
            ),
        }


class WeightLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='weight_logs',
    )
    date = models.DateField(default=timezone.localdate)
    weight = models.IntegerField()

    class Meta:
        ordering = ('-date',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'date'),
                name='unique_weight_log_per_user_per_day',
            ),
        ]

    def __str__(self):
        return f'{self.user} — {self.weight} kg on {self.date}'



