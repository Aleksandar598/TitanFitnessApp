from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from nutrition.models import Food
from users.models import CustomUser


class TestFood(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='undfined',
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

        self.food_data = {'name' : 'Banana',
                          'description' : 'A banana',
                          'user' : self.user,
                          'quantity' : 20,
                          'quantity_type' : 'g',
                          'protein' : 1,
                          'carbohydrates' : 1,
                          'fat' : 1,
                          }

    def test_invalid_quantity(self):
        data = self.food_data.copy()
        data['quantity'] = -1
        food = Food(**data)
        self.assertRaises(ValidationError, food.full_clean)

    def test_invalid_protein(self):
        data = self.food_data.copy()
        data['protein'] = -1
        food = Food(**data)
        self.assertRaises(ValidationError, food.full_clean)

    def test_invalid_carbohydrates(self):
        data = self.food_data.copy()
        data['carbohydrates'] = -1
        food = Food(**data)
        self.assertRaises(ValidationError, food.full_clean)

    def test_invalid_fat(self):
        data = self.food_data.copy()
        data['fat'] = -1
        food = Food(**data)
        self.assertRaises(ValidationError, food.full_clean)

    def test_invalid_total_grams(self):
        data = self.food_data.copy()
        data['quantity'] = 3
        data['protein'] = 1000
        food = Food(**data)
        self.assertRaises(ValidationError, food.full_clean)

    def test_calorie_auto_calculation(self):
        food = Food(**self.food_data)
        food.full_clean()
        self.assertEqual(food.calories, 17)

    def test_two_users_can_save_foods_with_the_same_name(self):
        Food.objects.create(**self.food_data)
        another_user = CustomUser.objects.create_user(
            username='another-user', email='another@example.com', password='misho',
            birth_date=date(1970, 1, 1), height=100, gender='male',
            current_weight=100, target_weight=100, fitness_goal=0, activity_level=1.2,
        )
        duplicate_food = Food(**{**self.food_data, 'user': another_user})
        duplicate_food.full_clean()

    def test_duplicate_food_name_for_the_same_user_is_invalid(self):
        Food.objects.create(**self.food_data)
        duplicate_food = Food(**self.food_data)
        self.assertRaises(ValidationError, duplicate_food.full_clean)
