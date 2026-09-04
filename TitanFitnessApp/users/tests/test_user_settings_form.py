from datetime import date

from django.test import TestCase

from users.forms.UserSettingsForm import UserSettingsForm
from users.models import CustomUser, FitnessGoal


class UserSettingsFormTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='settings-user',
            email='settings@example.com',
            password='password123',
            birth_date=date(1990, 1, 1),
            height=180,
            gender='male',
            current_weight=80,
            target_weight=80,
            fitness_goal=FitnessGoal.maintain.value,
            activity_level=1.2,
        )
        self.user_data = {
            'username': self.user.username,
            'email': self.user.email,
            'birth_date': self.user.birth_date,
            'height': self.user.height,
            'gender': self.user.gender,
            'current_weight': 80,
            'target_weight': 80,
            'activity_level': self.user.activity_level,
        }

    def test_settings_sets_lose_goal_when_target_weight_is_lower(self):
        form = UserSettingsForm(
            self.user_data | {'target_weight': 70},
            instance=self.user,
        )

        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertEqual(user.fitness_goal, FitnessGoal.lose.value)

    def test_settings_sets_maintain_goal_when_weights_are_equal(self):
        form = UserSettingsForm(
            self.user_data,
            instance=self.user,
        )

        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertEqual(user.fitness_goal, FitnessGoal.maintain.value)

    def test_settings_sets_gain_goal_when_target_weight_is_higher(self):
        form = UserSettingsForm(
            self.user_data | {'target_weight': 90},
            instance=self.user,
        )

        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertEqual(user.fitness_goal, FitnessGoal.gain.value)
