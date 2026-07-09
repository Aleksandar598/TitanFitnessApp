from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

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

    REQUIRED_FIELDS = ['email', 'birth_date', 'height', 'fitness_goal', 'current_weight', 'target_weight', 'gender', 'activity_level']

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

