from datetime import date

from django.test import TestCase
from django.urls import reverse

from nutrition.models import Food, FoodLog
from users.models import CustomUser


class CreateFoodLogViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='diary-user', email='diary@example.com', password='password123',
            birth_date=date(1990, 1, 1), height=180, gender='male',
            current_weight=80, target_weight=80, fitness_goal=0, activity_level=1.2,
        )
        self.other_user = CustomUser.objects.create_user(
            username='other-user', email='other@example.com', password='password123',
            birth_date=date(1990, 1, 1), height=180, gender='male',
            current_weight=80, target_weight=80, fitness_goal=0, activity_level=1.2,
        )
        self.food = Food.objects.create(
            user=self.user, name='Yogurt', quantity=100, quantity_type='g',
            protein=10, carbohydrates=4, fat=2, calories=74,
        )
        self.other_food = Food.objects.create(
            user=self.other_user, name='Other yogurt', quantity=100, quantity_type='g',
            protein=10, carbohydrates=4, fat=2, calories=74,
        )
        self.url = reverse('create_food_log')

    def test_page_requires_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_user_can_create_a_food_log_for_own_food(self):
        self.client.login(username=self.user.username, password='password123')
        response = self.client.post(self.url, {'food': self.food.id, 'quantity': 150, 'date': '2026-09-03'})

        self.assertRedirects(response, reverse('nutrition'))
        log = FoodLog.objects.get()
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.food, self.food)
        self.assertEqual(log.calories, 111)

    def test_user_cannot_create_a_food_log_for_another_users_food(self):
        self.client.login(username=self.user.username, password='password123')
        response = self.client.post(self.url, {'food': self.other_food.id, 'quantity': 100, 'date': '2026-09-03'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(FoodLog.objects.count(), 0)
