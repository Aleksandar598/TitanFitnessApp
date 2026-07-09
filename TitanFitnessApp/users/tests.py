from datetime import date

from django.test import TestCase

from .forms import CreateUserForm
from .models import CustomUser
from .validators import MINIMUM_HEIGHT, MAXIMUM_WEIGHT, MINIMUM_WEIGHT

# Create your tests here.

class CustomUserTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(  username='undfined',
                                                email='misho@misho.net',
                                                password='misho',
                                                birth_date=date(1970, 1, 1),
                                                height=100,
                                                gender='male',
                                                current_weight=100,
                                                target_weight=100,
                                                fitness_goal=0,
                                                activity_level=1.2,
                                              )
        self.gain_user = CustomUser.objects.create_user(username='someone',
                                                    email='misho@Old.net',
                                                    password='misho',
                                                    birth_date=date(1970, 1, 1),
                                                    height=100,
                                                    gender='male',
                                                    current_weight=100,
                                                    target_weight=150,
                                                    fitness_goal=250,
                                                    activity_level=1.2,
                                                   )
        self.lose_user = CustomUser.objects.create_user(username='Petar',
                                                        email='misho@New.net',
                                                        password='misho',
                                                        birth_date=date(1970, 1, 1),
                                                        height=100,
                                                        gender='male',
                                                        current_weight=100,
                                                        target_weight=50,
                                                        fitness_goal=-250,
                                                        activity_level=1.2,
                                                        )
        self.bmr = 10 * self.user.current_weight + 6.25 * self.user.height -5 * (date.today().year -  self.user.birth_date.year) + 5

    def testMaintainCalories(self):
        expected_calories = self.bmr * self.user.activity_level
        calories = self.user.daily_calorie_goal
        self.assertEqual(calories, expected_calories)

    def testGainCalories(self):
        expected_calories = self.bmr * self.gain_user.activity_level + self.gain_user.fitness_goal
        calories = self.gain_user.daily_calorie_goal
        self.assertEqual(calories, expected_calories)


    def testLoseCalories(self):
        expected_calories = self.bmr * self.lose_user.activity_level + self.lose_user.fitness_goal
        calories = self.lose_user.daily_calorie_goal
        self.assertEqual(calories, expected_calories)


class CreateUserFormTest(TestCase):
    def setUp(self):
        self.user_data = {   'username' : 'undfined',
                        'email' : 'misho@misho.net',
                        'password1' : 'TheGreatMisho',
                        'password2' : 'TheGreatMisho',
                        'birth_date' : date(1970, 1, 1),
                        'height' : 100,
                        'gender' : 'male',
                        'current_weight' : 100,
                        'target_weight': 100,
                        'fitness_goal': 0,
                        'activity_level': 1.2
        }
        self.user = CustomUser.objects.create_user(username='defined',
                                                   email='pesho@misho.net',
                                                   password='misho',
                                                   birth_date=date(1970, 1, 1),
                                                   height=100,
                                                   gender='male',
                                                   current_weight=100,
                                                   target_weight=100,
                                                   fitness_goal=0,
                                                   activity_level=1.2,
                                                   )

    def test_create_user_form_normal(self):
        form = CreateUserForm(self.user_data)
        self.assertTrue(form.is_valid())

    def test_create_user_form_taken_username(self):
        self.user_data['username'] = 'defined'
        form = CreateUserForm(self.user_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_create_user_form_taken_email(self):
        self.user_data['email'] = 'pesho@misho.net'
        form = CreateUserForm(self.user_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


    def test_create_user_form_invalid_birth_date(self):
        self.user_data['birth_date'] = date(5000, 11, 12)
        form = CreateUserForm(self.user_data)
        self.assertFalse(form.is_valid())
        self.assertIn('birth_date', form.errors)


    def test_create_user_form_invalid_height(self):
        self.user_data['height'] = MINIMUM_HEIGHT - 10
        form = CreateUserForm(self.user_data)
        self.assertFalse(form.is_valid())
        self.assertIn('height', form.errors)


    def test_create_user_form_too_low_current_weight(self):
        self.user_data['current_weight'] = MINIMUM_WEIGHT - 5
        form = CreateUserForm(self.user_data)
        self.assertFalse(form.is_valid())
        self.assertIn('current_weight', form.errors)


    def test_create_user_form_too_high_current_weight(self):
        self.user_data['current_weight'] = MAXIMUM_WEIGHT + 5
        form = CreateUserForm(self.user_data)
        self.assertFalse(form.is_valid())
        self.assertIn('current_weight', form.errors)


    def test_create_user_form_too_high_target_weight(self):
        self.user_data['target_weight'] = MAXIMUM_WEIGHT + 10
        form = CreateUserForm(self.user_data)
        self.assertFalse(form.is_valid())
        self.assertIn('target_weight', form.errors)

    def test_create_user_form_too_low_target_weight(self):
        self.user_data['target_weight'] = MINIMUM_WEIGHT - 5
        form = CreateUserForm(self.user_data)
        self.assertFalse(form.is_valid())
        self.assertIn('target_weight', form.errors)
