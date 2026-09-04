from datetime import date

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


# Create your models here.
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



