from datetime import date

from django.test import TestCase

from users.models import CustomUser, FitnessGoal


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

    def test_maintenance_macronutrient_goals(self):
        goals = self.user.daily_macronutrient_goals
        calorie_goal = self.user.daily_calorie_goal

        self.assertEqual(goals['calories'], round(calorie_goal))
        self.assertEqual(
            goals['carbohydrates'],
            round(calorie_goal * 0.50 / 4),
        )
        self.assertEqual(
            goals['protein'],
            round(calorie_goal * 0.20 / 4),
        )
        self.assertEqual(
            goals['fat'],
            round(calorie_goal * 0.30 / 9),
        )

    def test_fat_loss_macronutrient_goals(self):
        goals = self.lose_user.daily_macronutrient_goals
        calorie_goal = self.lose_user.daily_calorie_goal

        self.assertEqual(
            goals['carbohydrates'],
            round(calorie_goal * 0.40 / 4),
        )
        self.assertEqual(
            goals['protein'],
            round(calorie_goal * 0.30 / 4),
        )
        self.assertEqual(
            goals['fat'],
            round(calorie_goal * 0.30 / 9),
        )

    def test_muscle_gain_macronutrient_goals(self):
        goals = self.gain_user.daily_macronutrient_goals
        calorie_goal = self.gain_user.daily_calorie_goal

        self.assertEqual(
            goals['carbohydrates'],
            round(calorie_goal * 0.45 / 4),
        )
        self.assertEqual(
            goals['protein'],
            round(calorie_goal * 0.30 / 4),
        )
        self.assertEqual(
            goals['fat'],
            round(calorie_goal * 0.25 / 9),
        )

    def test_workout_calories_increase_daily_macronutrient_goals(self):
        goals = self.user.daily_macronutrient_goals_with_workout(400)
        base_goals = self.user.daily_macronutrient_goals

        self.assertEqual(goals['calories'], base_goals['calories'] + 400)
        self.assertEqual(
            goals['carbohydrates'],
            base_goals['carbohydrates'] + 60,
        )
        self.assertEqual(goals['protein'], base_goals['protein'] + 20)
        self.assertEqual(goals['fat'], base_goals['fat'] + 9)
