from datetime import date

from django.test import TestCase

from nutrition.models import Food, FoodLog
from users.models import CustomUser


class FoodLogTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='food-log-user', email='food-log@example.com', password='password123',
            birth_date=date(1990, 1, 1), height=180, gender='male',
            current_weight=80, target_weight=80, fitness_goal=0, activity_level=1.2,
        )
        self.food = Food.objects.create(
            user=self.user, name='Chicken breast', quantity=100, quantity_type='g',
            protein=31, carbohydrates=0, fat=3.6, calories=165,
        )

    def test_food_log_copies_consumed_portion_values(self):
        log = FoodLog.objects.create(user=self.user, food=self.food, quantity=150)

        self.assertEqual(log.food_name, 'Chicken breast')
        self.assertEqual(log.quantity_type, 'g')
        self.assertEqual(log.calories, 247.5)
        self.assertEqual(log.protein, 46.5)
        self.assertEqual(log.carbohydrates, 0)
        self.assertEqual(log.fat, 5.4)

    def test_food_log_is_kept_if_saved_food_is_deleted(self):
        log = FoodLog.objects.create(user=self.user, food=self.food, quantity=150)
        self.food.delete()

        log.refresh_from_db()
        self.assertIsNone(log.food)
        self.assertEqual(log.food_name, 'Chicken breast')
        self.assertEqual(log.calories, 247.5)
